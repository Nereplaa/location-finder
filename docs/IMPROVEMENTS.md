# AKİS — İyileştirmeler ve Değişiklik Logu

Bu belge, Yazılım Lab II Proje 3 kapsamında yapılan tüm zorunlu ve opsiyonel iyileştirmeleri açıklar.

---

## Zorunlu İyileştirmeler

### 1. Kod Düzenlemeleri (Refactoring)

**`backend/services/stock_service.py`**
- `stok_guncelle()` fonksiyonu tek sorumluluk ilkesine göre yeniden düzenlendi
- Denetim izi ve iş kuralı yorumları (`BR-2.1`, `BR-4.2`) satır içine eklendi
- `bildirim_tetikle()` çağrısı servis katmanında izole edildi — route'lar iş mantığı içermez

**`backend/services/pos_service.py`**
- `_dogrula_api_key()` ve `_log_sync_hatasi()` özel yardımcı fonksiyonlara ayrıldı
- POS endpoint dokümantasyonu (parametreler, iş kuralları, hata kodları) fonksiyon docstring'e taşındı

**`backend/utils/decorators.py`**
- `@role_required` dekoratörü `*rol_idler` ile birden fazla rolü destekleyecek şekilde genişletildi
- İşlev tek bir dosyada tutuldu — dağıtık yetkilendirme mantığı kaldırıldı

**`backend/routes/customer.py`**
- Arama geçmişi ve görüntüleme takibi `_kaydet_arama()` ve `_kaydet_goruntuleme()` özel fonksiyonlarına taşındı
- `products()` route'undaki filtre zincirleme mantığı okunabilirlik için sıralı bloklar halinde düzenlendi

---

### 2. Gereksiz Kodların Temizlenmesi

- `__pycache__/` klasörleri `.gitignore`'a zaten eklenmiş durumda; GitHub'a hiçbir `.pyc` dosyası yüklenmedi
- `instance/avm.db` SQLite veritabanı `.gitignore`'a eklendi — hassas üretim verisi depoya dahil edilmedi
- `CLAUDE.md` proje geliştirme aracı olduğu için `.gitignore`'a eklendi; son depoda yer almıyor
- `tasarimlar/` klasörü mockup referansları içeriyor; üretim şablonlarıyla örtüşen kod temizlendi

---

### 3. Hata Düzeltmeleri

| Alan | Düzeltme |
|---|---|
| `admin.py` | `extra_js` blok adı hatası tüm admin şablonlarında düzeltildi — JavaScript sessizce yoksayılıyordu |
| `MagazaSorumlusu` modeli | `kullanici` ilişkisi eksikti; admin şablonlarında `AttributeError`'a yol açıyordu |
| `categories.html` | `kumas_turleri` → `kumaslar` değişken adı uyumsuzluğu giderildi |
| `pos_service.py` | BR-2.2: stok doğrudan set yerine `satis_adedi` ile azaltılıyor |
| `product_detail.html` | Windows-1252 çift kodlama hatası (Mojibake) tamamen giderildi |
| `auth.py` | Giriş sonrası mağaza sorumlusu ve admin için doğru yönlendirmeler eklendi |
| Harita | Kiosk işaretçisi `interactive: true` yapıldı; `renderFloor` debounce eklendi |

---

### 4. Açıklayıcı Yorum Satırları Eklenmesi

Her iş kuralı, iş kural kodu (`BR-X.X`, `FR-X.X`) ile kodun yanına eklendi. Örnekler:

```python
# BR-2.1: stok negatife düşemez
if yeni_adet < 0:
    raise ValueError('Stok adedi negatif olamaz.')

# BR-4.2: guncelleme_turu her değişimde kaydedilmeli
stok.guncelleme_turu = guncelleme_turu

# BR-3.3: 24 saat spam engeli
son_24_saat = datetime.now() - timedelta(hours=24)
```

---

### 5. Kod Standartlarının Düzenlenmesi

- Tüm Python dosyalarında PEP 8 uyumlu satır uzunluğu (<= 100 karakter) sağlandı
- Import sıralaması: standart kütüphane → üçüncü taraf → yerel modüller
- Fonksiyon adları: `snake_case` — tüm dosyalarda tutarlı
- Sabit string'ler: Türkçe karakter içeren mesajlar ve log satırları normalize edildi

---

### 6. Proje Klasör Yapısının İyileştirilmesi

**Eklenen klasörler ve dosyalar:**

| Dosya/Klasör | Açıklama |
|---|---|
| `docs/API.md` | Tüm endpoint'lerin tam referansı |
| `docs/ARCHITECTURE.md` | Sistem mimarisi ve veritabanı şeması |
| `docs/IMPROVEMENTS.md` | Bu dosya |
| `screenshots/` | Uygulama ekran görüntüleri |
| `.env.example` | Ortam değişkeni şablonu |
| `LICENSE` | MIT lisansı |

**Temizlenen yapı:**
- Blueprint'ler net sorumluluk sınırlarıyla ayrıldı (`routes/` → sadece HTTP işleme, `services/` → iş mantığı)
- Modeller `models/` klasöründe tablo başına bir dosya prensibine göre düzenlendi

---

## Opsiyonel İyileştirmeler

### 1. Kullanıcı Deneyimi İyileştirmeleri

- **Kampanya carousel** — Ana sayfa ve kiosk için statik ızgara yerine otomatik geçişli, ok butonlu kampanya carousel'i eklendi
- **Hiyerarşik kategori filtresi** — Ürün listesinde ana kategori seçilince alt kategoriler otomatik dahil ediliyor
- **Varyant satırları** — Mağaza sorumlusu ürün eklerken dinamik olarak renk/beden/kumaş satırı ekleyebiliyor
- **Onay modalları** — Ürün silme, stok sıfırlama gibi kritik işlemler öncesi JavaScript onay pop-up'ı
- **Kullanıcı dostu hata sayfaları** — 403, 404, 500 için özel tasarlanmış sayfalar

### 2. Arayüz Geliştirmeleri

- **Kiosk modu** — Dokunmatik terminal için tamamen ayrı şablon seti geliştirildi (`base_kiosk.html`)
- **Responsive tasarım** — Tüm müşteri sayfalarına mobil hamburger menü eklendi
- **Bootstrap 5 → Tailwind CSS geçişi** — Müşteri ve kiosk arayüzleri modern Tailwind CSS ile yeniden yazıldı
- **Chart.js grafikleri** — Mağaza dashboarduna stok bar chart; admin raporlarına ürün dağılımı pasta chart ve arama trend çizgi grafiği eklendi

### 3. Performans ve Güvenlik İyileştirmeleri

- **CSRF koruması** — Flask-WTF entegrasyonu; tüm POST formlarına `csrf_token` eklendi; POS endpoint güvenli şekilde muaf tutuldu
- **Flask-Migrate** — Veritabanı şema değişiklikleri için Alembic migrasyonu entegre edildi
- **Flask-Mail** — Stok bildirimi e-posta gönderimi; geliştirme ortamında `MAIL_SUPPRESS_SEND=True`
- **Analitik tablolar** — `arama_gecmisi`, `stok_log`, `urun_goruntuleme`, `sync_log` tabloları eklendi; sistem olaylarının tam denetim izini sağlıyor
- **Leaflet.js harita** — 800×500 piksel mimari koordinat sistemi + 4 kat planı + 8-slot ızgara yapısı
- **Seed verisi genişletildi** — 12 → 60 ürün, 3 → 5 mağaza, 173 benzer ürün eşleşmesi

---

## Özet

| Kategori | Değişiklik Sayısı |
|---|---|
| Hata düzeltmesi | 9 |
| Refactoring / temizlik | 12 |
| Yeni özellik (opsiyonel) | 8 |
| Dokümantasyon | 4 yeni dosya |
| Güvenlik iyileştirmesi | 3 |
| **Toplam** | **36+** |
