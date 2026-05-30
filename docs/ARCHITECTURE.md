# AKİS — Sistem Mimarisi

---

## Genel Mimari

AKİS, **Blueprint tabanlı Flask monoliti** olarak tasarlanmıştır. Katmanlar arasındaki sorumluluklar net biçimde ayrılmıştır:

```
Tarayıcı / Kiosk / POS
        │
        ▼
┌─────────────────────────────────────────────────────┐
│                    Flask (WSGI)                      │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Routes  │  │ Services │  │     Models       │  │
│  │(Blueprint│→ │(İş mantı-│→ │(SQLAlchemy ORM)  │  │
│  │   HTTP)  │  │  ğı)     │  │                  │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                       │              │
└───────────────────────────────────────┼──────────────┘
                                        │
                                        ▼
                               SQLite / PostgreSQL
```

### Katman Sorumlulukları

| Katman | Konum | Sorumluluk |
|---|---|---|
| **Routes** | `backend/routes/` | HTTP isteği alma, form doğrulama, şablon render, yönlendirme |
| **Services** | `backend/services/` | İş kuralları, veri dönüşümü, yan etkiler (log, e-posta) |
| **Models** | `backend/models/` | Veritabanı şeması, ilişkiler, veri erişimi |
| **Utils** | `backend/utils/` | Yetkilendirme dekoratörü, giriş doğrulayıcılar |
| **Templates** | `frontend/templates/` | Jinja2 HTML şablonları, kullanıcı arayüzü |
| **Static** | `frontend/static/` | CSS, JavaScript, görseller |

---

## Blueprint Mimarisi

```
Flask App (create_app)
├── auth_bp          → prefix: /auth
├── customer_bp      → prefix: (kök)
├── manager_bp       → prefix: /manager
├── admin_bp         → prefix: /admin
├── kiosk_bp         → prefix: /kiosk
└── pos_bp           → prefix: (kök — /api/pos/*)
```

Her blueprint bağımsız olarak test edilebilir ve diğer blueprint'lerle doğrudan etkileşimi yoktur.

---

## Veritabanı Şeması (12 Tablo)

### Tablo İlişki Diyagramı

```
Roller ─────────────────────── Kullanicilar
  (1)                              (N)
                                    │
                        ┌───────────┤───────────────┐
                        │           │               │
                        ▼           ▼               ▼
                  MagazaSorumlu  BildirimTalebi  AramaGecmisi
                        │
                        ▼
                    Magazalar
                   /    │    \
                  /     │     \
                 ▼      ▼      ▼
             Stoklar  Kampanya  SyncLog
                │
                ▼
            StokLog

Urunler ───── Kategoriler
   │    └──── Markalar
   ├── UrunOzellikleri
   ├── BenzerUrunler
   └── UrunGoruntuleme
```

---

### Tablo Detayları

#### `Roller`
```
id          INTEGER  PK
rol_adi     TEXT     UNIQUE  NOT NULL
aciklama    TEXT
```
Sabit değerler: Müşteri (1), Mağaza Sorumlusu (2), Sistem Admini (3), Kiosk (4)

---

#### `Kullanicilar`
```
id                  INTEGER   PK
eposta              TEXT      UNIQUE  NOT NULL
sifre_hash          TEXT      NOT NULL          -- BCrypt
ad                  TEXT      NOT NULL
soyad               TEXT      NOT NULL
rol_id              INTEGER   FK→Roller
aktif_mi            BOOLEAN   DEFAULT True
olusturma_tarihi    DATETIME  DEFAULT now()
son_giris_tarihi    DATETIME
```

---

#### `Magazalar`
```
id                          INTEGER   PK
magaza_adi                  TEXT      NOT NULL
kat                         TEXT      NOT NULL
konum_kodu                  TEXT      UNIQUE  NOT NULL  -- BR-4.1
calisma_saati_baslangic     TEXT
calisma_saati_bitis         TEXT
aciklama                    TEXT
konum_x                     FLOAT                      -- Leaflet piksel koordinatı
konum_y                     FLOAT                      -- Leaflet piksel koordinatı
aktif_mi                    BOOLEAN   DEFAULT True
```

---

#### `MagazaSorumlulari`
```
id              INTEGER   PK
magaza_id       INTEGER   FK→Magazalar
kullanici_id    INTEGER   FK→Kullanicilar
atama_tarihi    DATETIME  DEFAULT now()
```
BR-1.1: Bir sorumlu yalnızca atandığı mağazayı yönetebilir.

---

#### `Kategoriler`
```
id                  INTEGER   PK
kategori_adi        TEXT      NOT NULL
ust_kategori_id     INTEGER   FK→Kategoriler (self-referential, nullable)
aktif_mi            BOOLEAN   DEFAULT True
```
Hiyerarşik yapı: Giyim → Kadın → Elbise

---

#### `Markalar`
```
id          INTEGER   PK
marka_adi   TEXT      UNIQUE  NOT NULL
aktif_mi    BOOLEAN   DEFAULT True
```

---

#### `Urunler`
```
id                  INTEGER   PK
urun_adi            TEXT      NOT NULL
aciklama            TEXT
gorsel_url          TEXT
marka_id            INTEGER   FK→Markalar
kategori_id         INTEGER   FK→Kategoriler
baz_fiyat           DECIMAL   NOT NULL
aktif_mi            BOOLEAN   DEFAULT True           -- BR-2.4
olusturma_tarihi    DATETIME  DEFAULT now()
```

---

#### `UrunOzellikleri`
```
id          INTEGER   PK
urun_id     INTEGER   FK→Urunler
renk        TEXT
beden       TEXT
kumas_turu  TEXT
ek_fiyat    DECIMAL   DEFAULT 0
```
Bir ürünün birden fazla varyantı olabilir.

---

#### `Stoklar`
```
id                      INTEGER   PK
urun_id                 INTEGER   FK→Urunler
magaza_id               INTEGER   FK→Magazalar
stok_adedi              INTEGER   DEFAULT 0  (>= 0)  -- BR-2.1
min_stok_seviyesi       INTEGER   DEFAULT 5
guncelleme_turu         TEXT      -- 'Manuel' | 'Otomatik'  BR-4.2
son_guncelleme_tarihi   DATETIME
son_guncelleyen_id      INTEGER   FK→Kullanicilar (nullable)
```

---

#### `Kampanyalar`
```
id                  INTEGER   PK
urun_id             INTEGER   FK→Urunler
magaza_id           INTEGER   FK→Magazalar
indirim_orani       DECIMAL   (0–100)
baslangic_tarihi    DATETIME  NOT NULL
bitis_tarihi        DATETIME  NOT NULL               -- BR-3.1: > baslangic
aktif_mi            BOOLEAN   DEFAULT True
```

---

#### `BildirimTalepleri`
```
id              INTEGER   PK
urun_id         INTEGER   FK→Urunler
kullanici_id    INTEGER   FK→Kullanicilar (nullable)
eposta          TEXT
telefon         TEXT
talep_tarihi    DATETIME  DEFAULT now()
bildirildi_mi   BOOLEAN   DEFAULT False
bildirim_tarihi DATETIME  (nullable)
```
BR-3.3: Aynı kullanıcı+ürün için 24 saat içinde yalnızca 1 aktif talep.

---

#### `BenzerUrunler`
```
id              INTEGER   PK
urun_id         INTEGER   FK→Urunler
benzer_urun_id  INTEGER   FK→Urunler
```

---

#### `AramaGecmisi` (Analitik)
```
id              INTEGER   PK
arama_metni     TEXT      NOT NULL
kullanici_id    INTEGER   FK→Kullanicilar (nullable)
kaynak          TEXT      DEFAULT 'web'  -- 'web' | 'kiosk'
tarih           DATETIME  DEFAULT now()
```

---

#### `StokLog` (Denetim İzi)
```
id                  INTEGER   PK
stok_id             INTEGER   FK→Stoklar
urun_id             INTEGER   FK→Urunler
magaza_id           INTEGER   FK→Magazalar
eski_adet           INTEGER
yeni_adet           INTEGER
guncelleme_turu     TEXT      -- 'Manuel' | 'Otomatik'
kullanici_id        INTEGER   FK→Kullanicilar (nullable)
tarih               DATETIME  DEFAULT now()
```

---

#### `UrunGoruntuleme` (Analitik)
```
id          INTEGER   PK
urun_id     INTEGER   FK→Urunler
kaynak      TEXT      DEFAULT 'web'  -- 'web' | 'kiosk'
tarih       DATETIME  DEFAULT now()
```

---

#### `SyncLog` (POS Hata Logu)
```
id          INTEGER   PK
magaza_id   INTEGER   FK→Magazalar (nullable)
hata_turu   TEXT      -- 'Stok Tutarsızlığı' | 'Kayıt Bulunamadı' | 'Sistem Hatası'
detay       TEXT
tarih       DATETIME  DEFAULT now()
```

---

## Kimlik Doğrulama ve Yetkilendirme Akışı

```
İstek gelir
    │
    ├── @login_required → oturum yoksa /auth/login'e yönlendir
    │
    └── @role_required(rol_id)
            │
            ├── current_user.is_authenticated? Hayır → 401
            │
            └── current_user.rol_id in rol_idler? Hayır → 403
                                                   Evet → Route çalışır
```

---

## Stok Güncelleme Akışı

```
Tetikleyici: Manuel (manager) veya Otomatik (POS webhook)
    │
    ▼
stock_service.stok_guncelle(urun_id, magaza_id, yeni_adet, tur)
    │
    ├── yeni_adet < 0? → ValueError (BR-2.1)
    │
    ├── Stok kaydı var mı? Hayır → Yeni kayıt oluştur
    │
    ├── stok.stok_adedi = yeni_adet
    ├── stok.guncelleme_turu = tur        (BR-4.2)
    ├── StokLog ekle                       (denetim izi)
    │
    └── stok_adedi > min_stok_seviyesi?
            Evet → bildirim_tetikle(urun_id)
                        │
                        └── BildirimTalebi.bildirildi_mi = True
                            + Flask-Mail gönder (üretimde)
```

---

## Harita Koordinat Sistemi

Leaflet.js `CRS.Simple` piksel koordinat sistemi kullanır. Harita 800×500 piksel boyutlarındadır.

```
(0,0) ─────────────────────────────── (800,0)
  │                                         │
  │    8-slot ızgara:                        │
  │    ÜST-1..4   (y: 50–175)               │
  │    Koridor Y  (y: 225–275)              │
  │    ALT-1..4   (y: 325–450)              │
  │                                         │
  │    Koridor X: (x: 385–415)              │
  │                                         │
(0,500) ─────────────────────────── (800,500)
```

Kiosk "Buradasınız" noktaları: Sol terminal (110, 250) · Sağ terminal (690, 250)

Her mağazanın `konum_x` ve `konum_y` değerleri bu koordinat sisteminde tanımlanmıştır.

---

## Güvenlik Mimarisi

| Tehdit | Önlem |
|---|---|
| CSRF saldırısı | Flask-WTF CSRFProtect — tüm POST formlarında `csrf_token` |
| Yetkisiz panel erişimi | `@role_required` dekoratörü — URL manipülasyonu HTTP 403 döner |
| Açık metin şifre | Werkzeug bcrypt hash — `generate_password_hash` / `check_password_hash` |
| Session ele geçirme | `PERMANENT_SESSION_LIFETIME = 1800` (30 dk otomatik son) |
| POS API kötüye kullanımı | `X-API-Key` başlığı doğrulama — eşleşmede 401 |
| SQL Injection | SQLAlchemy ORM parametrik sorgular kullanır |
| XSS | Jinja2 otomatik HTML escape |
