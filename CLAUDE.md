# CLAUDE.md — AKİS: AVM İçi Akıllı Ürün Bulma, Stok Takip ve Mağaza Yönlendirme Sistemi

Bu dosya, projenin ne olduğunu, ne çözdüğünü, nasıl geliştirileceğini ve güncel durumunu Claude'a anlatmak için hazırlanmıştır. Her yeni konuşmada bu dosyayı okuyarak projeye başla.

**Kaynak:** Yazılım Lab II — SRS Dokümanı (Grup: AKİS)  
**Rolümüz:** Bu projeyi geliştiren yazılım grubu (SRS dokümanını yazan grup değiliz)

---

## 1. PROJENİN AMACI VE ÇÖZDÜĞü SORUN

Modern AVM'lerde müşteriler binlerce ürün arasında arama yaparken ciddi sorunlar yaşar:
- Bir ürünün stokta olup olmadığını öğrenmek için mağazaya fiziksel olarak gitmek gerekmektedir.
- Hangi mağazada hangi ürünün hangi beden/renkte bulunduğu bilinmemektedir.
- Mağaza sorumluları stok verilerini merkezi bir sistemden yönetememektedir.
- Stok tükenen ürünler için müşteri bildirim mekanizması yoktur.

Bu sistem, "Akıllı AVM" konseptiyle bu sorunları çözer:
- Müşteri, kiosk veya mobil uygulama üzerinden ürün arar, stok durumunu görür ve mağazaya yönlendirilir.
- Mağaza sorumlusu, kendi mağazasındaki stokları yönetir ve kampanya tanımlar.
- Sistem admini, tüm AVM ekosistemini merkezi panelden yönetir.

---

## 2. KULLANICI ROLLERİ VE YETKİ MATRİSİ

Sistemde 3 kullanıcı rolü vardır:

| Rol | ID | Yetkiler |
|-----|----|----------|
| Müşteri / Ziyaretçi | 1 | Ürün arama, filtreleme, ürün detay görüntüleme, bildirim talebi oluşturma (kayıtlı), kampanya izleme |
| Mağaza Sorumlusu | 2 | Kendi mağazasına ürün ekle/güncelle, manuel stok güncelleme, kampanya tanımlama, mağaza dashboard |
| Sistem Admini | 3 | Mağaza ve kullanıcı yönetimi, kategori/parametre tanımlama, sistem geneli raporlama |

**Kritik:** Kayıtsız ziyaretçiler arama yapabilir ama bildirim talebi oluşturamaz (BR-1.2).

---

## 3. FONKSİYONEL GEREKSİNİMLER

### Müşteri / Ziyaretçi
| Kod | Gereksinim |
|-----|-----------|
| FR-1.1 | Ürün adı, marka veya kategori bazlı arama |
| FR-1.2 | Beden, renk, kumaş türü ve fiyat aralığına göre filtreleme |
| FR-1.3 | Ürün detayında: hangi mağaza, kat bilgisi, güncel fiyat, stok durumu (Var/Yok) |
| FR-1.4 | Stokta yok ürün için "Stok Gelince Haber Ver" talebi (iletişim bilgisi bırakma) |
| FR-1.5 | AVM genelindeki aktif kampanyaları ve indirimli ürünleri listeleme |

### Mağaza Sorumlusu
| Kod | Gereksinim |
|-----|-----------|
| FR-2.1 | Kendi mağazasına ürün ekleme, açıklama/görsel/fiyat güncelleme |
| FR-2.2 | Ürün stok adetlerini manuel olarak değiştirme |
| FR-2.3 | Belirli ürünler için indirim oranı + tarih aralığı ile kampanya oluşturma |
| FR-2.4 | Dashboard: en çok aranan ürünler, düşük stok uyarıları, görüntülenme istatistiği |

### Sistem Admini
| Kod | Gereksinim |
|-----|-----------|
| FR-3.1 | Yeni mağaza tanımlama, mağazalara sorumlu hesabı atama |
| FR-3.2 | Kategori ağacı, kumaş türleri, renk seçeneklerini yönetme |
| FR-3.3 | Arama trendleri, en popüler mağazalar, sistem performans raporları |

### Sistem Geneli
| Kod | Gereksinim |
|-----|-----------|
| FR-4.1 | Tüm kullanıcılar için güvenli Login mekanizması |
| FR-4.2 | RBAC: kullanıcılar yalnızca rolüne tanımlı ekranlara erişebilir |
| FR-4.3 | POS'tan gelen satış verisiyle otomatik stok azaltma |
| FR-4.4 | Otomatik sync başarısız olduğunda mağaza sorumlusuna ve admine uyarı |

---

## 4. FONKSİYONEL OLMAYAN GEREKSİNİMLER

### Performans
- NFR-1.1: Arama sonuçları (DB sorgusu + filtreleme dahil) maksimum **2 saniye**
- NFR-1.2: Aynı anda en az **100 aktif kullanıcı** (kiosk + mobil toplamı)
- NFR-1.3: Dashboard istatistik yükleme maksimum **3 saniye**

### Güvenlik
- NFR-2.1: Parolalar açık metin saklanamaz — **BCrypt veya PBKDF2** ile hash
- NFR-2.2: URL manipülasyonuyla yetkisiz panel erişimi engellenmeli (`@role_required` decorator)
- NFR-2.3: Belirli süre işlem yapılmayan oturum otomatik sonlandırılmalı (session timeout)

### Kullanılabilirlik
- NFR-3.1: Tüm arayüzler **responsive** — kiosk (yatay) ve mobil (dikey) uyumlu
- NFR-3.2: Kritik işlemler (ürün silme, stok sıfırlama) öncesi **onay pop-up** zorunlu
- NFR-3.3: Hata mesajları son kullanıcıya anlaşılır; teknik kod değil yönlendirici metin

### Sürdürülebilirlik
- NFR-4.1: Flask Blueprint mimarisi, modüler ve dökümante kod yapısı
- NFR-4.2: Veritabanı normalizasyona uygun, FK kısıtları tanımlı, soft delete (`aktif_mi`) uygulanmış

---

## 5. İŞ KURALLARI (KISITLAR)

### Kullanıcı & Yetki
- **BR-1.1** Mağaza sorumlusu yalnızca kendisine atanan mağazanın verilerini yönetebilir
- **BR-1.2** Kayıtsız ziyaretçi bildirim talebi oluşturamaz, yönetim panellerine erişemez
- **BR-1.3** Admin, sorumlu şifrelerini göremez; yalnızca şifre sıfırlama yapabilir

### Ürün & Stok
- **BR-2.1** `stok_adedi` negatife düşemez; 0'a ulaşınca durum otomatik "Tükendi"
- **BR-2.2** POS verisi > mevcut stok olursa işlem yapılır, tutarsızlık loga yazılır
- **BR-2.3** Ürün, sistemde tanımlı olmayan kategori veya markaya atanamaz
- **BR-2.4** `aktif_mi=False` olan ürün arama sonuçlarında gösterilmez

### Kampanya & Bildirim
- **BR-3.1** `bitis_tarihi` >= `baslangic_tarihi` olmak zorunda
- **BR-3.2** Bildirimler `stok_adedi > min_stok_seviyesi` koşulu sağlandığında otomatik tetiklenir
- **BR-3.3** Aynı kullanıcı + aynı ürün için 24 saat içinde yalnızca 1 bildirim talebi

### Sistem & Veri Bütünlüğü
- **BR-4.1** Her mağaza için `konum_kodu` veritabanında UNIQUE olmalı
- **BR-4.2** Stok güncellemelerinde `guncelleme_turu` alanı 'Manuel' veya 'Otomatik' olarak kaydedilmeli

---

## 6. VERİTABANI ŞEMASI (12 TABLO)

Tüm tablolar ilişkisel yapıda olup soft delete (`aktif_mi` boolean) uygulanır.

### 1. `Roller`
```
id (PK), rol_adi (UNIQUE), aciklama
```

### 2. `Kullanicilar`
```
id (PK), eposta (UNIQUE), sifre_hash, ad, soyad,
rol_id (FK→Roller), aktif_mi (bool, default=True),
olusturma_tarihi, son_giris_tarihi
```

### 3. `Magazalar`
```
id (PK), magaza_adi, kat, konum_kodu (UNIQUE),
calisma_saati_baslangic, calisma_saati_bitis,
aciklama, aktif_mi (bool, default=True)
```
> BR-4.1: Her mağazanın konum_kodu benzersiz olmalıdır.

### 4. `MagazaSorumlulari`
```
id (PK), magaza_id (FK→Magazalar), kullanici_id (FK→Kullanicilar),
atama_tarihi
```
> BR-1.1: Sorumlu yalnızca atandığı mağazayı yönetebilir.

### 5. `Kategoriler`
```
id (PK), kategori_adi, ust_kategori_id (FK→Kategoriler, nullable),
aktif_mi (bool, default=True)
```
> Hiyerarşik yapı: Giyim → Kadın → Elbise

### 6. `Markalar`
```
id (PK), marka_adi (UNIQUE), aktif_mi (bool, default=True)
```

### 7. `Urunler`
```
id (PK), urun_adi, aciklama, gorsel_url,
marka_id (FK→Markalar), kategori_id (FK→Kategoriler),
baz_fiyat (Decimal), aktif_mi (bool, default=True),
olusturma_tarihi
```
> BR-2.3: Ürün, tanımsız kategori veya markaya atanamaz.
> BR-2.4: aktif_mi=False olan ürün arama sonuçlarında görünmez.

### 8. `UrunOzellikleri`
```
id (PK), urun_id (FK→Urunler), renk, beden, kumas_turu, ek_fiyat (Decimal)
```

### 9. `Stoklar`
```
id (PK), urun_id (FK→Urunler), magaza_id (FK→Magazalar),
stok_adedi (INT, >= 0), min_stok_seviyesi (INT),
guncelleme_turu (ENUM: 'Manuel', 'Otomatik'),
son_guncelleme_tarihi, son_guncelleyen_id (FK→Kullanicilar, nullable)
```
> BR-2.1: stok_adedi negatife düşemez; 0'a ulaşınca ürün "Tükendi" durumuna geçer.
> BR-4.2: guncelleme_turu her güncellemede kayıt altına alınmalıdır.

### 10. `Kampanyalar`
```
id (PK), urun_id (FK→Urunler), magaza_id (FK→Magazalar),
indirim_orani (Decimal, 0-100), baslangic_tarihi (DateTime),
bitis_tarihi (DateTime), aktif_mi (bool, default=True)
```
> BR-3.1: bitis_tarihi > baslangic_tarihi zorunludur (DB constraint veya validator).

### 11. `BildirimTalepleri`
```
id (PK), urun_id (FK→Urunler), kullanici_id (FK→Kullanicilar, nullable),
eposta, telefon, talep_tarihi (DateTime),
bildirildi_mi (bool, default=False), bildirim_tarihi (DateTime, nullable)
```
> BR-3.2: stok_adedi > min_stok_seviyesi olduğunda tetiklenir.
> BR-3.3: Aynı kullanıcı+ürün kombinasyonu için 24 saat içinde tek talep.

### 12. `BenzerUrunler`
```
id (PK), urun_id (FK→Urunler), benzer_urun_id (FK→Urunler)
```

**Ek tablolar (isteğe bağlı — henüz uygulanmadı):**
- `arama_gecmisi`: Kullanıcı arama logları (arama_metni, kullanici_id, tarih) — trend analizi için
- `stok_log`: Stok değişim geçmişi (eski_adet, yeni_adet, guncelleme_turu, tarih)

---

## 7. TEKNOLOJİ STACK'İ

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.x + Flask (Blueprint mimarisi) |
| ORM | SQLAlchemy (Code-First) |
| Veritabanı | SQLite (geliştirme) → PostgreSQL (üretim) |
| Frontend | HTML5 + CSS3 + JavaScript (Responsive/Bootstrap) |
| Şablon Motoru | Jinja2 |
| Kimlik Doğrulama | Flask-Login + Werkzeug parola hash |
| POS Entegrasyonu | REST API (otomatik stok sync) |
| Dashboard Grafikleri | Chart.js (stok grafikleri, trend istatistikleri) — henüz uygulanmadı |

---

## 8. PROJE DİZİN YAPISI

```
YLP/
├── backend/
│   ├── __init__.py
│   ├── app.py                    # Flask app factory (create_app)
│   ├── config.py                 # SQLite/PostgreSQL config
│   ├── extensions.py             # db, login_manager instance'ları
│   ├── models/
│   │   ├── __init__.py           # Tüm modelleri import eder
│   │   ├── roller.py             # Roller tablosu
│   │   ├── kullanicilar.py       # Kullanicilar tablosu
│   │   ├── magazalar.py          # Magazalar tablosu
│   │   ├── magaza_sorumlulari.py # MagazaSorumlulari tablosu
│   │   ├── kategoriler.py        # Kategoriler tablosu
│   │   ├── markalar.py           # Markalar tablosu
│   │   ├── urunler.py            # Urunler tablosu
│   │   ├── urun_ozellikleri.py   # UrunOzellikleri tablosu
│   │   ├── stoklar.py            # Stoklar tablosu
│   │   ├── kampanyalar.py        # Kampanyalar tablosu
│   │   ├── bildirim_talepleri.py # BildirimTalepleri tablosu
│   │   └── benzer_urunler.py     # BenzerUrunler tablosu
│   ├── routes/
│   │   ├── auth.py               # /auth/login, /auth/logout, /auth/register
│   │   ├── customer.py           # /, /products, /api/search, /api/products/<id>
│   │   ├── manager.py            # /manager/* (dashboard, ürün, stok, kampanya)
│   │   └── admin.py              # /admin/* (mağaza, kullanıcı, kategori, rapor)
│   ├── services/
│   │   ├── stock_service.py      # Stok güncelleme iş mantığı + bildirim tetikleme
│   │   ├── notification_service.py # Bildirim talep işaretleme
│   │   └── pos_service.py        # POS otomatik sync (/api/pos/stock-update)
│   └── utils/
│       ├── decorators.py         # @role_required(rol_id) decorator
│       └── validators.py         # E-posta/şifre doğrulama
├── frontend/
│   ├── templates/
│   │   ├── base.html             # Ana layout — navbar, footer
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── customer/
│   │   │   ├── index.html        # Ana sayfa: arama + kategoriler
│   │   │   ├── products.html     # Ürün listeleme + filtreler
│   │   │   ├── product_detail.html # Ürün detay + stok + benzer ürünler
│   │   │   ├── campaigns.html    # Aktif kampanyalar
│   │   │   └── notification_modal.html
│   │   ├── manager/
│   │   │   ├── dashboard.html    # Sorumlu dashboard
│   │   │   ├── products.html     # Ürün listesi + stok güncelleme
│   │   │   └── campaign_form.html # Kampanya oluşturma
│   │   └── admin/
│   │       ├── dashboard.html    # Admin dashboard
│   │       ├── stores.html       # Mağaza yönetimi
│   │       ├── users.html        # Kullanıcı yönetimi
│   │       ├── categories.html   # Kategori/parametre yönetimi
│   │       └── reports.html      # Raporlar
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
├── tasarimlar/                   # Statik HTML mockup tasarımları (referans)
│   ├── 1_ana_sayfa.html
│   ├── 2_urun_detay.html
│   ├── 3_magaza_dashboard.html
│   ├── 4_urunler_liste.html
│   ├── 5_stok_yonetimi.html
│   └── 6_admin_paneli.html
├── instance/                     # SQLite veritabanı dosyası (avm.db)
├── run.bat                       # Windows'ta sunucu başlatma script'i
├── venv/                         # Python sanal ortam
├── CLAUDE.md                     # ← Bu dosya
├── eski_CLAUDE.md                # Eski versiyon (arşiv)
└── yeni_CLAUDE.md                # Yeni versiyon (arşiv)
```

---

## 9. API ENDPOINT ŞEMASI

```
# Auth (Blueprint: auth, prefix: /auth)
POST   /auth/login                    # Giriş
GET    /auth/logout                   # Çıkış (@login_required)
GET/POST /auth/register               # Kayıt

# Müşteri (Blueprint: customer, prefix: /)
GET    /                               # Ana sayfa
GET    /products                       # Ürün arama + filtreleme
GET    /api/search                     # Arama (aynı endpoint)
GET    /api/products/<id>              # Ürün detay
GET    /api/campaigns                  # Aktif kampanyalar
POST   /api/notifications             # Bildirim talebi (@login_required)

# Mağaza Sorumlusu (Blueprint: manager, prefix: /manager)
GET    /manager/dashboard              # Dashboard (@role_required(2))
GET/POST /manager/products             # Ürün listesi + ekleme
POST   /manager/products/<id>/stock    # Stok güncelleme
POST   /manager/products/<id>/deactivate  # Ürün pasife alma
POST   /manager/products/<id>/reset-stock # Stok sıfırlama
GET/POST /manager/campaigns            # Kampanya listesi + oluşturma
POST   /manager/campaigns/<id>/delete  # Kampanya silme (soft delete)

# Admin (Blueprint: admin, prefix: /admin)
GET    /admin/dashboard                # Dashboard (@role_required(3))
GET/POST /admin/stores                 # Mağaza listesi + ekleme
POST   /admin/stores/<id>/assign       # Sorumlu atama
POST   /admin/stores/<id>/deactivate   # Mağaza pasife alma
POST   /admin/stores/<id>/activate     # Mağaza aktifleştirme
GET/POST /admin/users                  # Kullanıcı listesi + ekleme
POST   /admin/users/<id>/deactivate    # Kullanıcı pasife alma
POST   /admin/users/<id>/activate      # Kullanıcı aktifleştirme
POST   /admin/users/<id>/reset-password # Şifre sıfırlama
GET/POST /admin/categories             # Kategori yönetimi
POST   /admin/categories/<id>/delete   # Kategori silme (soft delete)
GET    /admin/reports                  # Raporlar

# POS Webhook (Blueprint: pos, prefix: /)
POST   /api/pos/stock-update           # Otomatik stok sync (JSON)
```

---

## 10. TEMEL İŞ AKIŞLARI

### Müşteri: Ürün Arama ve Yönlendirme
1. Kullanıcı kiosk/mobil'de ürün adı veya filtreleri girer.
2. Backend, `urunler` + `stoklar` + `magazalar` tablolarını join'leyerek sonuçları döner.
3. Stokta var → mağaza kat/konum bilgisi ve "Mağazaya Git" butonu gösterilir.
4. Stokta yok → benzer ürünler listelenir + "Stok Gelince Haber Ver" formu sunulur.

### Bildirim Talebi
1. Kayıtlı kullanıcı "Haber Ver" formunu doldurur.
2. Backend, aynı kullanıcı + aynı ürün için son 24 saatte talep var mı kontrol eder (BR-3.3).
3. Yoksa `bildirim_talepleri` tablosuna kayıt eklenir.
4. POS üzerinden stok güncellendiğinde, sistem bekleyen talepleri kontrol eder ve eşleşenlere bildirim gönderir.

### Mağaza Sorumlusu: Manuel Stok Güncelleme
1. Sorumlu, yönetim panelinden ürün seçer ve yeni stok adedini girer.
2. Backend, kullanıcının o mağazaya yetkisi olup olmadığını kontrol eder.
3. `stoklar` tablosu güncellenir, `guncelleme_turu = "Manuel"` olarak işaretlenir.
4. `stock_service.py` üzerinden `bildirim_tetikle()` çağrılır.

### POS ile Otomatik Stok Güncelleme
1. Mağaza POS sistemi satış gerçekleşince `/api/pos/stock-update` endpoint'ine POST atar.
2. Backend, veri formatını doğrular; ürün ve mağaza eşleşmesini kontrol eder.
3. Stok yeterliyse azaltılır, `guncelleme_turu = "Otomatik"` set edilir.
4. Stok minimum seviyenin üstüne çıktıysa bekleyen bildirim talepleri tetiklenir.
5. Hata durumunda log'a kaydedilir.

---

## 11. ARAYÜZ YAPISI

### Müşteri / Kiosk
- **Ana Sayfa:** Merkezi arama çubuğu + Kategoriler + Popüler Mağazalar
- **Ürün Listeleme:** Sol filtre paneli (renk, beden, marka, stok) + Sağ ürün kartları
- **Ürün Detay:** Görsel, fiyat, özellikler, mağaza kat/konum, "Yol Tarifi Göster" butonu
- **Bildirim Formu:** Pop-up — isim + e-posta/telefon girişi

### Mağaza Sorumlusu Paneli
- **Dashboard:** Toplam ürün, kritik stok uyarıları (kırmızı), en çok görüntülenen grafik
- **Ürün/Stok Listesi:** "Hızlı Stok Güncelle" butonu + Manuel/Otomatik ikonları
- **Kampanya Formu:** Ürün seçimi + indirim % + takvim (tarih aralığı)

### Admin Paneli
- **Genel Dashboard:** Aktif mağaza sayısı, kullanıcı sayısı, hata logları
- **Mağaza & Kullanıcı Yönetimi:** Mağaza ekle, kat/konum ata, sorumlu yetkilendir
- **Parametre Yönetimi:** Renk, beden, kumaş, kategori ağacı düzenleme

---

## 12. GELİŞTİRME AŞAMALARI VE GÜNCEL DURUM

### Aşama 1 — Temel Kurulum
- [x] Flask projesi oluştur, blueprint mimarisini kur
- [x] `config.py`'da dev/prod ayarlarını tanımla (SQLite dev için)
- [x] SQLAlchemy modellerini yaz (12 tablo)
- [x] Flask-Migrate kurulumu (extensions.py + app.py + run.bat otomatik init)
- [x] Seed data: örnek roller, admin kullanıcı, 3-5 mağaza, kategoriler

### Aşama 2 — Auth Sistemi
- [x] Kayıt ve giriş sayfaları (e-posta + şifre)
- [x] Flask-Login ile session yönetimi
- [x] Werkzeug ile şifre hashleme
- [x] Rol tabanlı erişim dekoratörleri (`@role_required`)
- [x] Yetkisiz erişim denemelerinde 401/403 dönüşü

### Aşama 3 — Müşteri Arayüzü
- [x] Ana sayfa: arama çubuğu + kategori + kampanyalar
- [x] Arama + filtreleme endpoint'i ve sonuç listesi
- [x] Ürün detay sayfası (stok bilgisi + mağaza konumu + benzer ürünler)
- [x] Kampanya listesi sayfası
- [x] Bildirim talebi formu ve backend kontrolü (24 saat kuralı)

### Aşama 4 — Mağaza Sorumlusu Paneli
- [x] Dashboard (ürün sayısı, düşük stok uyarıları)
- [x] Ürün listesi ve hızlı stok güncelleme
- [x] Yeni ürün ekleme formu
- [x] Kampanya oluşturma formu (tarih aralığı + indirim oranı)
- [x] Ürün pasife alma (soft delete)

### Aşama 5 — Admin Paneli
- [x] Mağaza listesi ve yeni mağaza ekleme (benzersiz konum_kodu kontrolü)
- [x] Kullanıcı listesi, ekleme, aktif/pasif, şifre sıfırlama
- [x] Kategori yönetimi (hiyerarşik)
- [x] Temel raporlar (mağaza sayısı, kullanıcı sayısı, düşük stok)
- [x] Marka yönetimi (CRUD — /admin/brands)
- [ ] Gelişmiş raporlar (arama trendleri, popüler mağazalar, grafikler)

### Aşama 6 — API ve POS Entegrasyonu
- [x] `/api/pos/stock-update` POST endpoint'i (JSON body)
- [x] API key token doğrulaması (X-API-Key header veya query param — pos_service.py)
- [x] Hata durumunda log kaydı
- [x] Stok sonrası bekleyen bildirim taleplerini kontrol ve işaretleme
- [x] Flask-Mail entegrasyonu — notification_service.py e-posta gönderimi (dev'de suppress)

### Aşama 7 — Test ve Polishing
- [x] Seed data script'i (`seed.py` — 3 mağaza, 12 ürün, kampanyalar)
- [x] Tüm iş kurallarının edge case testleri (BR-1.1, BR-2.1, BR-2.2, BR-3.1, BR-3.3, BR-4.1)
- [x] Responsive tasarım kontrolü — mobil hamburger menü tüm müşteri sayfalarına eklendi
- [x] Kritik işlemler için onay modalları (JavaScript — data-onay attribute)
- [x] Kullanıcı dostu hata sayfaları (403, 404, 500)
- [x] CSRF koruması (Flask-WTF — tüm POST formlarına csrf_token, POS blueprint exempt)
- [x] Chart.js dashboard grafikleri (manager: stok bar chart, admin/reports: ürün dağılımı + kampanya donut)

---

## 13. GELİŞTİRME KURALLARI

- Her route dosyası Flask **Blueprint** olarak yapılandırılmalı.
- DB iş mantığı doğrudan route içinde yapılmaz; `services/` katmanı üzerinden.
- `@role_required(rol_id)` decorator'ı yetkisiz erişimi engeller.
- Stok güncellemelerinde `guncelleme_turu` parametresi her zaman iletilmeli.
- Soft delete: kayıt silme yerine `aktif_mi=False` kullan.
- Parola hash için `werkzeug.security` kullan — açık metin asla.
- POS API endpoint'leri `/api/` prefix'i altında olmalı ve diğer blueprint'lerden ayrı tutulmalıdır.
- Her feature için önce modeli, sonra service'i, sonra route'u, sonra template'i yaz.
- Kritik hatalar (POS sync başarısız) `app.logger` ile loglanmalı.
- Blueprint'leri birbirinden bağımsız tut.

---

## 14. CLAUDE'UN KENDİNİ GÜNCELLEME KURALI

**Her geliştirme adımının sonunda bu dosyayı güncelle.**

Bir özellik tamamlandığında, bir dosya oluşturulduğunda veya bir karar değiştiğinde:

1. Bölüm 12'deki ilgili görevin başındaki `[ ]` kutusunu `[x]` ile işaretle.
2. Bölüm 15'teki "Proje Güncel Durumu" tablosunu güncelle.
3. Eğer mimari bir karar değiştiyse (yeni tablo, blueprint değişikliği) ilgili bölümü düzenle.

---

## 15. PROJE GÜNCEL DURUMU

Bu tablo her geliştirme adımından sonra Claude tarafından güncellenir.

| Tarih | Tamamlanan | Notlar |
|-------|------------|--------|
| 2026-04-20 | CLAUDE.md birleştirildi | eski + yeni versiyonlar merge edildi, proje durumu analiz edildi |
| 2026-04-20 | Admin panel düzeltildi | base_admin.html oluşturuldu (Bootstrap), tüm admin template'leri güncellendi |
| 2026-04-20 | Marka yönetimi eklendi | /admin/brands CRUD — brands.html template |
| 2026-04-20 | Hata sayfaları eklendi | 403, 404, 500 handler'ları + template'leri |
| 2026-04-20 | Seed data tamamlandı | seed.py — 3 mağaza, 12 ürün, 6 marka, kampanyalar |
| 2026-04-20 | Route hataları düzeltildi | admin dashboard değişken isimleri, manager dashboard eksik değişkenler |
| 2026-04-20 | CSRF koruması eklendi | Flask-WTF CSRFProtect, tüm POST formlarına csrf_token, POS endpoint exempt |
| 2026-04-20 | POS API token doğrulama | X-API-Key header kontrolü, config'den POS_API_KEY |
| 2026-04-20 | Flask-Mail entegrasyonu | notification_service.py e-posta gönderimi, dev'de MAIL_SUPPRESS_SEND=True |
| 2026-04-20 | Flask-Migrate kurulumu | extensions.py + app.py + run.bat otomatik db init |
| 2026-04-20 | Chart.js grafikleri | Manager dashboard stok bar chart, admin/reports ürün+kampanya grafikleri |
| 2026-04-20 | Admin reports düzeltildi | dusuk_stoklar list olarak döndürüldü, magaza_ozet verisi eklendi |
| 2026-04-20 | categories.html hatası giderildi | delete_param endpoint eksikliği, renk/beden/kumaş string'e dönüştürüldü, kumas_turleri → kumaslar |
| 2026-04-20 | POS service düzeltildi | satis_adedi ile stok azaltma (BR-2.2), stok_adedi doğrudan set yerine |
| 2026-04-20 | Edge case testleri geçti | BR-1.1, BR-2.1, BR-2.2, BR-3.1, BR-3.3, BR-4.1 doğrulandı |
| 2026-04-20 | Frontend sync + responsive audit tamamlandı | base_manager.html oluşturuldu (Bootstrap 5); manager/products.html + campaign_form.html Bootstrap base'e geçirildi; campaigns.html Tailwind'e rewrite edildi; customer.py'de marka_id/kategori_id/stok/magaza_id parametre uyumsuzlukları düzeltildi; product_detail stockModal hidden+style çakışması giderildi; tüm müşteri sayfalarına (index/products/product_detail/campaigns) mobil hamburger menü eklendi; filter form'da kategori_id+magaza_id hidden input korunması sağlandı |
| 2026-04-30 | Auth sayfaları Tailwind'e dönüştürüldü | login.html + register.html — Bootstrap/bi-icon bağımlılığı tamamen kaldırıldı; glass-panel + gradient buton + Material Symbols + Tailwind renk token'ları kullanıldı; yerel flash bloğu kaldırıldı (base.html yönetiyor); şifre min-length 6→8 düzeltildi; body_class flex-center layout |

**Tamamlanma Oranı:** ~%100  
**Aktif Aşama:** Tamamlandı  
**Son Tamamlanan:** Auth sayfaları (login/register) Tailwind glassmorphism tasarımına dönüştürüldü  
**Kalan Görevler:**
- Gelişmiş raporlar (arama trendleri, grafikler) — isteğe bağlı

---

## 16. BAĞIMLILIKLAR (requirements.txt içeriği)

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Bcrypt==1.0.1
Flask-Migrate==4.0.7
Flask-WTF==1.2.1
Flask-Mail==0.10.0
SQLAlchemy==2.0.30
python-dotenv==1.0.1
```
