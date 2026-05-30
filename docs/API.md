# AKİS — REST API Referansı

Bu belge, AKİS sisteminin tüm HTTP endpoint'lerini açıklar.

---

## Kimlik Doğrulama

Sistemde iki ayrı kimlik doğrulama mekanizması kullanılır:

| Mekanizma | Kullanıldığı Yer |
|---|---|
| **Flask-Login oturumu** | Web arayüzü — tüm tarayıcı rotaları |
| **X-API-Key başlığı** | `POST /api/pos/stock-update` — POS entegrasyonu |

POS anahtarı `.env` dosyasındaki `POS_API_KEY` değeriyle eşleşmelidir.

---

## Kimlik Doğrulama Rotaları

### `GET /auth/login`
Giriş sayfasını döner.

### `POST /auth/login`
Kullanıcıyı oturum açtırır.

**Form parametreleri:**

| Alan | Zorunlu | Açıklama |
|---|---|---|
| `eposta` | Evet | Kayıtlı e-posta adresi |
| `sifre` | Evet | Kullanıcı şifresi |

**Yönlendirmeler:**

| Rol | Yönlendirme |
|---|---|
| Müşteri (1) | `/` |
| Mağaza Sorumlusu (2) | `/manager/dashboard` |
| Sistem Admini (3) | `/admin/dashboard` |
| Kiosk (4) | `/kiosk/` |

---

### `GET /auth/logout`
Oturumu sonlandırır ve `/auth/login` adresine yönlendirir.

*Auth: Giriş gerekli*

---

### `GET /auth/register`
Kayıt sayfasını döner.

### `POST /auth/register`
Yeni müşteri hesabı oluşturur.

**Form parametreleri:**

| Alan | Zorunlu | Açıklama |
|---|---|---|
| `ad` | Evet | Ad |
| `soyad` | Evet | Soyad |
| `eposta` | Evet | Benzersiz e-posta |
| `sifre` | Evet | En az 8 karakter |
| `sifre_tekrar` | Evet | Şifre doğrulama |

---

## Müşteri Rotaları

### `GET /`
AVM ana sayfasını döner: arama çubuğu, üst kategoriler, aktif kampanyalar.

---

### `GET /products`
### `GET /api/search`
Ürün arama ve filtreleme sayfasını döner.

**Query parametreleri:**

| Parametre | Tip | Açıklama |
|---|---|---|
| `q` | string | Ürün adı veya marka bazlı arama metni |
| `kategori_id` | int | Kategori filtresi (alt kategoriler otomatik dahil) |
| `marka_id` | int[] | Birden fazla marka filtresi (tekrarlanabilir) |
| `magaza_id` | int | Belirli mağaza filtresi |
| `renk` | string[] | Renk filtresi (tekrarlanabilir) |
| `beden` | string[] | Beden filtresi (tekrarlanabilir) |
| `kumas_turu` | string[] | Kumaş türü filtresi (tekrarlanabilir) |
| `fiyat_min` | float | Minimum fiyat |
| `fiyat_max` | float | Maksimum fiyat |
| `stok` | string | `var` → sadece stokta olanları göster |

**Not:** Arama her çağrıda `arama_gecmisi` tablosuna kayıt ekler (analitik için).

---

### `GET /api/products/<urun_id>`
Ürün detay sayfasını döner.

**Path parametresi:** `urun_id` — integer

**İçerik:**
- Ürün bilgileri ve varyantları
- Mağaza bazlı stok durumu
- Aktif kampanya (varsa)
- Benzer ürünler (DB kaydı yoksa kategori/marka bazlı otomatik fallback)
- Interaktif AVM haritası için tüm mağaza koordinatları

**Not:** Her çağrıda `urun_goruntuleme` tablosuna kayıt ekler.

---

### `GET /api/campaigns`
Aktif kampanyalar sayfasını döner. Bitiş tarihi geçmiş kampanyalar filtrelenir.

---

### `POST /api/notifications`
Stok bildirim talebi oluşturur.

*Auth: Giriş gerekli (BR-1.2)*

**Form parametreleri:**

| Alan | Zorunlu | Açıklama |
|---|---|---|
| `urun_id` | Evet | Bildirim istenilen ürün ID'si |
| `eposta` | Hayır | İletişim e-postası |
| `telefon` | Hayır | İletişim telefonu |

**İş kuralları:**
- BR-3.3: Aynı kullanıcı + aynı ürün için son 24 saat içinde talep varsa reddedilir

---

## Mağaza Sorumlusu Rotaları

> Tüm `/manager/*` rotaları `@role_required(2)` ile korunmaktadır.  
> BR-1.1: Sorumlu yalnızca kendi atandığı mağazanın verilerine erişebilir.

### `GET /manager/dashboard`
Dashboard sayfasını döner.

**İçerik:** toplam ürün sayısı · düşük stok uyarıları · bugünkü görüntülenme · son 10 stok hareketi · TOP 5 popüler ürün · 7 günlük görüntülenme grafiği

---

### `GET /manager/products`
Mağazanın ürün listesini döner.

**Query parametreleri:**

| Parametre | Açıklama |
|---|---|
| `q` | Ürün adı arama |
| `stok_filtre` | `tukendi` · `kritik` · `normal` |

---

### `POST /manager/products`
Mağazaya yeni ürün ekler.

**Form parametreleri:** `urun_adi`, `aciklama`, `gorsel_url`, `marka_id`, `kategori_id`, `baz_fiyat`, `stok_adedi`, `min_stok_seviyesi`, opsiyonel varyant satırları (renk/beden/kumaş/ek_fiyat)

---

### `POST /manager/products/<urun_id>/update`
Mevcut ürünü günceller.

**Form parametreleri:** `aciklama`, `gorsel_url`, `baz_fiyat`, `marka_id`, `kategori_id`, `min_stok_seviyesi`

---

### `POST /manager/products/<urun_id>/stock`
Ürün stok adedini günceller (manuel güncelleme — BR-4.2).

**Form parametresi:** `stok_adedi` — integer (>= 0)

---

### `POST /manager/products/<urun_id>/deactivate`
Ürünü pasife alır (soft delete — BR-2.4: arama sonuçlarından gizler).

---

### `POST /manager/products/<urun_id>/reset-stock`
Ürün stok adedini 0'a sıfırlar.

---

### `GET /manager/campaigns`
Mağazanın kampanya listesini döner.

### `POST /manager/campaigns`
Yeni kampanya oluşturur.

**Form parametreleri:** `urun_id`, `indirim_orani` (0–100), `baslangic_tarihi`, `bitis_tarihi`

**İş kuralı:** BR-3.1 — `bitis_tarihi` >= `baslangic_tarihi` zorunludur.

---

### `POST /manager/campaigns/<kampanya_id>/delete`
Kampanyayı siler (soft delete).

---

## Sistem Admini Rotaları

> Tüm `/admin/*` rotaları `@role_required(3)` ile korunmaktadır.

### `GET /admin/dashboard`
Admin dashboard: aktif mağaza · kullanıcı sayıları · bugünkü arama · ısı haritası verisi · POS sync hataları

---

### `GET /admin/stores`
Mağaza listesi.

### `POST /admin/stores`
Yeni mağaza ekler.

**Form parametreleri:** `magaza_adi`, `kat`, `konum_kodu` (UNIQUE), `calisma_saati_baslangic`, `calisma_saati_bitis`, `aciklama`

---

### `POST /admin/stores/<magaza_id>/update`
Mağaza bilgilerini günceller.

### `POST /admin/stores/<magaza_id>/assign`
Mağazaya sorumlu atar.

**Form parametresi:** `kullanici_id`

### `POST /admin/stores/<magaza_id>/deactivate`
Mağazayı pasife alır.

### `POST /admin/stores/<magaza_id>/activate`
Mağazayı aktifleştirir.

---

### `GET /admin/users`
Kullanıcı listesi.

**Query parametreleri:** `q` (arama), `rol_id` (rol filtresi)

### `POST /admin/users`
Yeni kullanıcı ekler.

### `POST /admin/users/<kullanici_id>/role`
Kullanıcının rolünü değiştirir.

### `POST /admin/users/<kullanici_id>/deactivate`
Kullanıcıyı pasife alır.

### `POST /admin/users/<kullanici_id>/activate`
Kullanıcıyı aktifleştirir.

### `POST /admin/users/<kullanici_id>/reset-password`
Kullanıcının şifresini sıfırlar.

**Form parametresi:** `yeni_sifre`

---

### `GET /admin/categories`
Hiyerarşik kategori listesi.

### `POST /admin/categories`
Yeni kategori ekler.

**Form parametreleri:** `kategori_adi`, `ust_kategori_id` (opsiyonel)

### `POST /admin/categories/<kategori_id>/update`
Kategori adını günceller.

### `POST /admin/categories/<kategori_id>/delete`
Kategoriyi pasife alır (soft delete).

---

### `GET /admin/brands`
Marka listesi.

### `POST /admin/brands`
Yeni marka ekler.

### `POST /admin/brands/<marka_id>/activate`
Markayı aktifleştirir.

### `POST /admin/brands/<marka_id>/deactivate`
Markayı pasife alır.

---

### `GET /admin/reports`
Gelişmiş raporlar sayfası.

**İçerik:** EN ÇOK aranan 10 terim · popüler mağazalar · kategori dağılımı · 7 günlük arama trendi

---

## Kiosk Rotaları

> Tüm `/kiosk/*` rotaları `@role_required(4)` ile korunmaktadır.

### `GET /kiosk/`
Kiosk ana sayfası — büyük arama, kategori kartları, kampanya carousel

### `GET /kiosk/products`
Sayfalı ürün listesi (8 ürün/sayfa)

### `GET /kiosk/products/<urun_id>`
Ürün detay — Leaflet harita dahil, bildirim formu yok

### `GET /kiosk/campaigns`
Aktif kampanya listesi

---

## POS Entegrasyon API'si

### `POST /api/pos/stock-update`

POS sisteminden gelen satış olayını işler ve stoku otomatik günceller.

**CSRF:** Bu endpoint Flask-WTF'den muaftır; API key ile korunur.

**Headers:**

```
X-API-Key: <POS_API_KEY>
Content-Type: application/json
```

**Request body:**

```json
{
  "urun_id": 42,
  "magaza_id": 3,
  "satis_adedi": 2
}
```

| Alan | Tip | Zorunlu | Açıklama |
|---|---|---|---|
| `urun_id` | integer | Evet | Satılan ürün ID'si |
| `magaza_id` | integer | Evet | Satışın yapıldığı mağaza ID'si |
| `satis_adedi` | integer (> 0) | Evet | Satılan adet (stoktan düşülür) |

**Başarılı yanıt — HTTP 200:**

```json
{
  "durum": "basarili",
  "stok_adedi": 8
}
```

**Hata yanıtları:**

| HTTP Kodu | Sebep |
|---|---|
| 400 | Eksik veya geçersiz parametre |
| 401 | Geçersiz API anahtarı |
| 404 | Ürün/mağaza kombinasyonu stok kaydı bulunamadı |
| 500 | Sunucu hatası (SyncLog'a yazılır) |

**İş kuralları:**
- BR-2.2: `satis_adedi` > mevcut stok ise stok 0'a çekilir, tutarsızlık `sync_log` tablosuna yazılır
- Güncelleme sonrası `stok_adedi > min_stok_seviyesi` ise bekleyen bildirim talepleri tetiklenir
