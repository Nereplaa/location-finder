"""
seed.py — AKİS Projesi Örnek Veri Doldurma Script'i

Kullanım:
    python seed.py

Oluşturulan veriler:
- 3 Rol
- 1 Admin, 5 Mağaza Sorumlusu, 2 Müşteri
- 5 Mağaza (LC Waikiki, Teknoloji Dünyası, Ayakkabı Center, Zara, Koton)
- Kategori ağacı
- 10 Marka
- 50+ ürün, her beden/renk/kumaş türüne geniş kapsama
- 8 Kampanya
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from backend.app import create_app
from backend.extensions import db
from backend.models.roller import Rol
from backend.models.kullanicilar import Kullanici
from backend.models.magazalar import Magaza
from backend.models.magaza_sorumlulari import MagazaSorumlusu
from backend.models.kategoriler import Kategori
from backend.models.markalar import Marka
from backend.models.urunler import Urun
from backend.models.urun_ozellikleri import UrunOzelligi
from backend.models.stoklar import Stok
from backend.models.kampanyalar import Kampanya
from backend.models.bildirim_talepleri import BildirimTalebi
from backend.models.benzer_urunler import BenzerUrun
from backend.models.arama_gecmisi import AramaGecmisi
from backend.models.stok_log import StokLog
from backend.models.urun_goruntuleme import UrunGoruntuleme
from backend.models.sync_log import SyncLog

app = create_app('development')


def temizle():
    """Tüm tabloları drop edip yeniden oluştur — model değişikliklerini yansıtır."""
    db.drop_all()
    db.create_all()
    print("[*] Tablolar yeniden oluşturuldu.")


def roller_olustur():
    roller = [
        Rol(id=1, rol_adi='Müşteri',          aciklama='AVM ziyaretçisi / alışverişçi'),
        Rol(id=2, rol_adi='Mağaza Sorumlusu', aciklama='Mağaza stok ve ürün yöneticisi'),
        Rol(id=3, rol_adi='Admin',             aciklama='Sistem yöneticisi'),
        Rol(id=4, rol_adi='Kiosk',             aciklama='AVM kiosk terminali'),
    ]
    db.session.add_all(roller)
    db.session.commit()
    print("[+] Roller oluşturuldu.")


def kullanicilar_olustur():
    kullanicilar = [
        Kullanici(eposta='admin@avm.com',      sifre_hash=generate_password_hash('a'),
                  ad='Sistem',   soyad='Yöneticisi', rol_id=3),
        Kullanici(eposta='sorumlu1@avm.com',   sifre_hash=generate_password_hash('a'),
                  ad='Ahmet',    soyad='Yılmaz',     rol_id=2),
        Kullanici(eposta='sorumlu2@avm.com',   sifre_hash=generate_password_hash('a'),
                  ad='Ayşe',     soyad='Kaya',       rol_id=2),
        Kullanici(eposta='sorumlu3@avm.com',   sifre_hash=generate_password_hash('a'),
                  ad='Mehmet',   soyad='Demir',      rol_id=2),
        Kullanici(eposta='sorumlu4@avm.com',   sifre_hash=generate_password_hash('a'),
                  ad='Elif',     soyad='Arslan',     rol_id=2),
        Kullanici(eposta='sorumlu5@avm.com',   sifre_hash=generate_password_hash('a'),
                  ad='Can',      soyad='Öztürk',     rol_id=2),
        Kullanici(eposta='musteri1@mail.com',  sifre_hash=generate_password_hash('a'),
                  ad='Fatma',    soyad='Çelik',      rol_id=1),
        Kullanici(eposta='musteri2@mail.com',  sifre_hash=generate_password_hash('a'),
                  ad='Ali',      soyad='Şahin',      rol_id=1),
        Kullanici(eposta='kiosk@avm.com',      sifre_hash=generate_password_hash('a'),
                  ad='Kiosk',    soyad='Terminal',   rol_id=4),
    ]
    db.session.add_all(kullanicilar)
    db.session.commit()
    print("[+] Kullanıcılar oluşturuldu.")
    return {k.eposta: k for k in kullanicilar}


def magazalar_olustur(kullanici_map):
    magazalar = [
        Magaza(magaza_adi='LC Waikiki',        kat='1', konum_kodu='A-101',
               calisma_saati_baslangic='10:00', calisma_saati_bitis='22:00',
               aciklama='Giyim ve aksesuar mağazası',
               konum_x=120, konum_y=128),
        Magaza(magaza_adi='Teknoloji Dünyası', kat='2', konum_kodu='B-210',
               calisma_saati_baslangic='10:00', calisma_saati_bitis='22:00',
               aciklama='Elektronik ve teknoloji ürünleri',
               konum_x=120, konum_y=128),
        Magaza(magaza_adi='Ayakkabı Center',   kat='0', konum_kodu='Z-001',
               calisma_saati_baslangic='10:00', calisma_saati_bitis='21:30',
               aciklama='Her marka ayakkabı ve çanta',
               konum_x=120, konum_y=128),
        Magaza(magaza_adi='Zara',              kat='1', konum_kodu='A-105',
               calisma_saati_baslangic='10:00', calisma_saati_bitis='22:00',
               aciklama='Güncel moda ve giyim koleksiyonu',
               konum_x=508, konum_y=128),
        Magaza(magaza_adi='Koton',             kat='0', konum_kodu='Z-015',
               calisma_saati_baslangic='10:00', calisma_saati_bitis='21:00',
               aciklama='Sezonun en şık giyim parçaları',
               konum_x=508, konum_y=128),
    ]
    db.session.add_all(magazalar)
    db.session.commit()
    print("[+] Mağazalar oluşturuldu.")

    atamalar = [
        MagazaSorumlusu(magaza_id=magazalar[0].id, kullanici_id=kullanici_map['sorumlu1@avm.com'].id),
        MagazaSorumlusu(magaza_id=magazalar[1].id, kullanici_id=kullanici_map['sorumlu2@avm.com'].id),
        MagazaSorumlusu(magaza_id=magazalar[2].id, kullanici_id=kullanici_map['sorumlu3@avm.com'].id),
        MagazaSorumlusu(magaza_id=magazalar[3].id, kullanici_id=kullanici_map['sorumlu4@avm.com'].id),
        MagazaSorumlusu(magaza_id=magazalar[4].id, kullanici_id=kullanici_map['sorumlu5@avm.com'].id),
    ]
    db.session.add_all(atamalar)
    db.session.commit()
    print("[+] Mağaza sorumlu atamaları yapıldı.")
    return magazalar


def kategoriler_olustur():
    giyim    = Kategori(kategori_adi='Giyim')
    elektro  = Kategori(kategori_adi='Elektronik')
    ayakkabi = Kategori(kategori_adi='Ayakkabı & Çanta')
    db.session.add_all([giyim, elektro, ayakkabi])
    db.session.flush()

    alt = [
        Kategori(kategori_adi='Erkek Giyim',    ust_kategori_id=giyim.id),
        Kategori(kategori_adi='Kadın Giyim',    ust_kategori_id=giyim.id),
        Kategori(kategori_adi='Çocuk Giyim',    ust_kategori_id=giyim.id),
        Kategori(kategori_adi='Telefon',         ust_kategori_id=elektro.id),
        Kategori(kategori_adi='Bilgisayar',      ust_kategori_id=elektro.id),
        Kategori(kategori_adi='Aksesuar',        ust_kategori_id=elektro.id),
        Kategori(kategori_adi='Spor Ayakkabı',   ust_kategori_id=ayakkabi.id),
        Kategori(kategori_adi='Klasik Ayakkabı', ust_kategori_id=ayakkabi.id),
        Kategori(kategori_adi='Çanta',           ust_kategori_id=ayakkabi.id),
    ]
    db.session.add_all(alt)
    db.session.commit()
    print("[+] Kategoriler oluşturuldu.")
    return {k.kategori_adi: k for k in [giyim, elektro, ayakkabi] + alt}


def markalar_olustur():
    marka_adlari = ['LC Waikiki', 'Zara', 'H&M', 'Koton', 'Mavi',
                    'Samsung', 'Apple', 'Nike', 'Adidas', 'Puma']
    markalar_list = [Marka(marka_adi=ad) for ad in marka_adlari]
    db.session.add_all(markalar_list)
    db.session.commit()
    print("[+] Markalar oluşturuldu.")
    return {m.marka_adi: m for m in markalar_list}


def _ekle_urun(d, marka_map, kategori_map):
    """Tek ürün + özellikleri + stok kaydını ekler, flush yapar."""
    urun = Urun(
        urun_adi=d['adi'],
        aciklama=d.get('aciklama', ''),
        marka_id=marka_map[d['marka']].id,
        kategori_id=kategori_map[d['kat']].id,
        baz_fiyat=d['fiyat'],
    )
    db.session.add(urun)
    db.session.flush()

    for renk, beden, kumas, ek in d.get('ozellikler', []):
        db.session.add(UrunOzelligi(
            urun_id=urun.id, renk=renk, beden=beden, kumas_turu=kumas, ek_fiyat=ek
        ))

    db.session.add(Stok(
        urun_id=urun.id,
        magaza_id=d['magaza'].id,
        stok_adedi=d['stok'],
        min_stok_seviyesi=d['min'],
        guncelleme_turu='Manuel',
    ))
    return urun


def urunler_ve_stoklar_olustur(magazalar, kategori_map, marka_map):
    m1, m2, m3, m4, m5 = magazalar  # LC W, Teknoloji, Ayakkabı, Zara, Koton

    # ─── LC WAİKİKİ (m1) — 14 ürün ────────────────────────────────────────────
    lcw = [
        {'adi': 'Erkek Basic T-Shirt',        'marka': 'LC Waikiki', 'kat': 'Erkek Giyim',
         'fiyat': 99.90,  'magaza': m1, 'stok': 25, 'min': 5,
         'ozellikler': [('Beyaz','S','Pamuk',0),('Beyaz','M','Pamuk',0),('Siyah','M','Pamuk',0),('Siyah','L','Pamuk',0),('Gri','XL','Pamuk',0)]},

        {'adi': 'Kadın Yazlık Elbise',        'marka': 'LC Waikiki', 'kat': 'Kadın Giyim',
         'fiyat': 249.90, 'magaza': m1, 'stok': 12, 'min': 3,
         'ozellikler': [('Lacivert','S','Viskon',0),('Lacivert','M','Viskon',0),('Pembe','M','Viskon',15),('Krem','L','Viskon',0)]},

        {'adi': 'Çocuk Eşofman Takımı',       'marka': 'LC Waikiki', 'kat': 'Çocuk Giyim',
         'fiyat': 179.90, 'magaza': m1, 'stok': 8,  'min': 5,
         'ozellikler': [('Mavi','4-5 Yaş','Pamuk',0),('Gri','6-7 Yaş','Pamuk',0),('Kırmızı','8-9 Yaş','Pamuk',0)]},

        {'adi': 'Erkek Slim Fit Jean',         'marka': 'Mavi',       'kat': 'Erkek Giyim',
         'fiyat': 399.90, 'magaza': m1, 'stok': 0,  'min': 5,
         'ozellikler': [('Lacivert','28','Denim',0),('Lacivert','30','Denim',0),('Siyah','30','Denim',0),('Gri','32','Denim',0)]},

        {'adi': 'Kadın Keten Gömlek',          'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 219.90, 'magaza': m5, 'stok': 15, 'min': 4,
         'ozellikler': [('Krem','XS','Keten',0),('Krem','S','Keten',0),('Bej','M','Keten',10),('Beyaz','L','Keten',0)]},

        {'adi': 'Erkek Spor Şort',             'marka': 'LC Waikiki', 'kat': 'Erkek Giyim',
         'fiyat': 129.90, 'magaza': m1, 'stok': 3,  'min': 5,
         'ozellikler': [('Siyah','M','Polyester',0),('Lacivert','L','Polyester',0),('Gri','XL','Polyester',0)]},

        {'adi': 'Çocuk Baskılı Sweatshirt',   'marka': 'LC Waikiki', 'kat': 'Çocuk Giyim',
         'fiyat': 149.90, 'magaza': m1, 'stok': 20, 'min': 5,
         'ozellikler': [('Mavi','8-9 Yaş','Triko',0),('Pembe','10-11 Yaş','Triko',0),('Kırmızı','6-7 Yaş','Triko',0)]},

        {'adi': 'Kadın Kadife Blazer',         'marka': 'H&M',        'kat': 'Kadın Giyim',
         'fiyat': 549.90, 'magaza': m1, 'stok': 6,  'min': 2,
         'ozellikler': [('Siyah','XS','Kadife',0),('Bordo','S','Kadife',0),('Lacivert','M','Kadife',0)]},

        {'adi': 'Erkek Keten Gömlek',          'marka': 'H&M',        'kat': 'Erkek Giyim',
         'fiyat': 299.90, 'magaza': m1, 'stok': 10, 'min': 3,
         'ozellikler': [('Beyaz','S','Keten',0),('Mavi','M','Keten',0),('Bej','L','Keten',0),('Kahverengi','XL','Keten',0)]},

        {'adi': 'Kadın Saten Bluz',            'marka': 'H&M',        'kat': 'Kadın Giyim',
         'fiyat': 189.90, 'magaza': m1, 'stok': 0,  'min': 4,
         'ozellikler': [('Gri','XS','Saten',0),('Pembe','S','Saten',0),('Krem','M','Saten',0)]},

        {'adi': 'Erkek Triko Kazak',           'marka': 'Mavi',       'kat': 'Erkek Giyim',
         'fiyat': 349.90, 'magaza': m1, 'stok': 4,  'min': 3,
         'ozellikler': [('Lacivert','M','Triko',0),('Gri','L','Triko',0),('Siyah','XL','Triko',0),('Bordo','XXL','Triko',0)]},

        {'adi': 'Çocuk Yazlık Şort',           'marka': 'LC Waikiki', 'kat': 'Çocuk Giyim',
         'fiyat': 89.90,  'magaza': m1, 'stok': 18, 'min': 5,
         'ozellikler': [('Mavi','4-5 Yaş','Denim',0),('Beyaz','6-7 Yaş','Denim',0),('Turuncu','8-9 Yaş','Pamuk',0)]},

        {'adi': 'Kadın Şifon Midi Elbise',     'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 329.90, 'magaza': m5, 'stok': 9,  'min': 3,
         'ozellikler': [('Yeşil','S','Şifon',0),('Pembe','M','Şifon',0),('Bordo','L','Şifon',0)]},

        {'adi': 'Erkek Polyester Yağmurluk',   'marka': 'LC Waikiki', 'kat': 'Erkek Giyim',
         'fiyat': 599.90, 'magaza': m1, 'stok': 2,  'min': 3,
         'ozellikler': [('Lacivert','M','Polyester',0),('Siyah','L','Polyester',0),('Kırmızı','XL','Polyester',0)]},
    ]

    # ─── TEKNOLOJİ DÜNYASI (m2) — 8 ürün ──────────────────────────────────────
    tek = [
        {'adi': 'Samsung Galaxy A55',          'marka': 'Samsung',    'kat': 'Telefon',
         'fiyat': 14999.00, 'magaza': m2, 'stok': 7,  'min': 2,
         'ozellikler': [('Siyah',None,None,0),('Beyaz',None,None,0),('Lacivert',None,None,500)]},

        {'adi': 'Apple iPhone 15',             'marka': 'Apple',      'kat': 'Telefon',
         'fiyat': 39999.00, 'magaza': m2, 'stok': 3,  'min': 2,
         'ozellikler': [('Siyah',None,None,0),('Gri',None,None,0),('Pembe',None,None,1000)]},

        {'adi': 'Samsung USB-C Şarj Aleti',    'marka': 'Samsung',    'kat': 'Aksesuar',
         'fiyat': 249.00,  'magaza': m2, 'stok': 30, 'min': 10,
         'ozellikler': [('Siyah',None,None,0),('Beyaz',None,None,0)]},

        {'adi': 'Bluetooth Kulaklık Pro',      'marka': 'Samsung',    'kat': 'Aksesuar',
         'fiyat': 1299.00, 'magaza': m2, 'stok': 2,  'min': 3,
         'ozellikler': [('Siyah',None,None,0),('Beyaz',None,None,0)]},

        {'adi': 'Apple Watch SE',              'marka': 'Apple',      'kat': 'Aksesuar',
         'fiyat': 12499.00, 'magaza': m2, 'stok': 5,  'min': 2,
         'ozellikler': [('Gümüş',None,None,0),('Siyah',None,None,0)]},

        {'adi': 'Powerbank 20000 mAh',         'marka': 'Samsung',    'kat': 'Aksesuar',
         'fiyat': 799.00,  'magaza': m2, 'stok': 0,  'min': 5,
         'ozellikler': [('Siyah',None,None,0),('Beyaz',None,None,0)]},

        {'adi': 'Laptop Kılıfı 15"',           'marka': 'Apple',      'kat': 'Aksesuar',
         'fiyat': 349.00,  'magaza': m2, 'stok': 12, 'min': 4,
         'ozellikler': [('Gri',None,None,0),('Siyah',None,None,0)]},

        {'adi': 'Samsung Galaxy Tab A9',       'marka': 'Samsung',    'kat': 'Bilgisayar',
         'fiyat': 9999.00, 'magaza': m2, 'stok': 4,  'min': 2,
         'ozellikler': [('Gri',None,None,0),('Gümüş',None,None,500)]},
    ]

    # ─── AYAKKABI CENTER (m3) — 10 ürün ────────────────────────────────────────
    aya = [
        {'adi': 'Nike Air Max 90',             'marka': 'Nike',       'kat': 'Spor Ayakkabı',
         'fiyat': 3499.00, 'magaza': m3, 'stok': 10, 'min': 3,
         'ozellikler': [('Beyaz','38',None,0),('Beyaz','39',None,0),('Siyah','40',None,0),('Siyah','42',None,200)]},

        {'adi': 'Adidas Ultraboost 22',        'marka': 'Adidas',     'kat': 'Spor Ayakkabı',
         'fiyat': 4299.00, 'magaza': m3, 'stok': 6,  'min': 3,
         'ozellikler': [('Siyah','39',None,0),('Gri','40',None,0),('Lacivert','41',None,0),('Kırmızı','42',None,0)]},

        {'adi': 'Puma Sneaker Kadın',          'marka': 'Puma',       'kat': 'Spor Ayakkabı',
         'fiyat': 1799.00, 'magaza': m3, 'stok': 0,  'min': 4,
         'ozellikler': [('Pembe','36',None,0),('Beyaz','37',None,0),('Lacivert','38',None,0)]},

        {'adi': 'Nike Revolution 6',           'marka': 'Nike',       'kat': 'Spor Ayakkabı',
         'fiyat': 2199.00, 'magaza': m3, 'stok': 4,  'min': 3,
         'ozellikler': [('Siyah','40',None,0),('Gri','41',None,0),('Lacivert','42',None,0),('Kırmızı','43',None,0)]},

        {'adi': 'Adidas Stan Smith',           'marka': 'Adidas',     'kat': 'Klasik Ayakkabı',
         'fiyat': 2799.00, 'magaza': m3, 'stok': 8,  'min': 3,
         'ozellikler': [('Beyaz','37',None,0),('Beyaz','38',None,0),('Yeşil','39',None,0),('Siyah','40',None,0)]},

        {'adi': 'Puma Classic Loafer',         'marka': 'Puma',       'kat': 'Klasik Ayakkabı',
         'fiyat': 1499.00, 'magaza': m3, 'stok': 3,  'min': 3,
         'ozellikler': [('Kahverengi','40',None,0),('Siyah','41',None,0),('Bej','42',None,0)]},

        {'adi': 'Nike Spor Sandalet',          'marka': 'Nike',       'kat': 'Klasik Ayakkabı',
         'fiyat': 999.00,  'magaza': m3, 'stok': 0,  'min': 4,
         'ozellikler': [('Siyah','36',None,0),('Gri','37',None,0),('Lacivert','38',None,0)]},

        {'adi': 'Adidas Terrex Bot',           'marka': 'Adidas',     'kat': 'Spor Ayakkabı',
         'fiyat': 3999.00, 'magaza': m3, 'stok': 5,  'min': 2,
         'ozellikler': [('Siyah','40',None,0),('Kahverengi','41',None,0),('Lacivert','42',None,0),('Gri','43',None,0)]},

        {'adi': 'Puma Future Rider',           'marka': 'Puma',       'kat': 'Spor Ayakkabı',
         'fiyat': 2299.00, 'magaza': m3, 'stok': 7,  'min': 3,
         'ozellikler': [('Beyaz','38',None,0),('Siyah','39',None,0),('Kırmızı','40',None,0),('Turuncu','41',None,0)]},

        {'adi': 'Nike Topuklu Bot',            'marka': 'Nike',       'kat': 'Klasik Ayakkabı',
         'fiyat': 2599.00, 'magaza': m3, 'stok': 2,  'min': 3,
         'ozellikler': [('Siyah','36',None,0),('Bordo','37',None,0),('Lacivert','38',None,0)]},
    ]

    # ─── ZARA (m4) — 14 ürün ───────────────────────────────────────────────────
    zara = [
        {'adi': 'Zara Viskon Midi Elbise',     'marka': 'Zara',       'kat': 'Kadın Giyim',
         'fiyat': 799.90,  'magaza': m4, 'stok': 10, 'min': 3,
         'ozellikler': [('Siyah','XS','Viskon',0),('Bej','S','Viskon',0),('Bordo','M','Viskon',0),('Krem','L','Viskon',0)]},

        {'adi': 'Zara İpek Bluz',              'marka': 'Zara',       'kat': 'Kadın Giyim',
         'fiyat': 649.90,  'magaza': m4, 'stok': 6,  'min': 2,
         'ozellikler': [('Beyaz','XS','İpek',0),('Krem','S','İpek',0),('Pembe','M','İpek',0)]},

        {'adi': 'Zara Erkek Slim Chino',       'marka': 'Zara',       'kat': 'Erkek Giyim',
         'fiyat': 699.90,  'magaza': m4, 'stok': 8,  'min': 3,
         'ozellikler': [('Bej','30','Pamuk',0),('Kahverengi','32','Pamuk',0),('Lacivert','34','Pamuk',0)]},

        {'adi': 'Zara Kadife Mini Etek',       'marka': 'Zara',       'kat': 'Kadın Giyim',
         'fiyat': 499.90,  'magaza': m4, 'stok': 0,  'min': 3,
         'ozellikler': [('Siyah','XS','Kadife',0),('Bordo','S','Kadife',0),('Yeşil','M','Kadife',0)]},

        {'adi': 'Zara Şifon Gömlek',           'marka': 'Zara',       'kat': 'Kadın Giyim',
         'fiyat': 549.90,  'magaza': m4, 'stok': 14, 'min': 4,
         'ozellikler': [('Beyaz','S','Şifon',0),('Mavi','M','Şifon',0),('Lacivert','L','Şifon',0),('Krem','XL','Şifon',0)]},

        {'adi': 'Zara Erkek Denim Ceket',      'marka': 'Zara',       'kat': 'Erkek Giyim',
         'fiyat': 1099.90, 'magaza': m4, 'stok': 5,  'min': 2,
         'ozellikler': [('Lacivert','S','Denim',0),('Gri','M','Denim',0),('Siyah','L','Denim',0)]},

        {'adi': 'Zara Kadın Triko Kazak',      'marka': 'Zara',       'kat': 'Kadın Giyim',
         'fiyat': 849.90,  'magaza': m4, 'stok': 3,  'min': 3,
         'ozellikler': [('Krem','XS','Triko',0),('Bej','S','Triko',0),('Gri','M','Triko',0),('Lacivert','L','Triko',0)]},

        {'adi': 'Zara Erkek Keten Pantolon',   'marka': 'Zara',       'kat': 'Erkek Giyim',
         'fiyat': 749.90,  'magaza': m4, 'stok': 11, 'min': 3,
         'ozellikler': [('Bej','28','Keten',0),('Kahverengi','30','Keten',0),('Krem','32','Keten',0)]},

        {'adi': 'Zara Saten Gecelik Elbise',   'marka': 'Zara',       'kat': 'Kadın Giyim',
         'fiyat': 699.90,  'magaza': m4, 'stok': 0,  'min': 2,
         'ozellikler': [('Krem','S','Saten',0),('Pembe','M','Saten',0),('Siyah','L','Saten',0)]},

        {'adi': 'Zara Çocuk Baskılı Tişört',  'marka': 'Zara',       'kat': 'Çocuk Giyim',
         'fiyat': 199.90,  'magaza': m4, 'stok': 22, 'min': 5,
         'ozellikler': [('Beyaz','4-5 Yaş','Pamuk',0),('Kırmızı','6-7 Yaş','Pamuk',0),('Mavi','8-9 Yaş','Pamuk',0),('Yeşil','10-11 Yaş','Pamuk',0)]},

        {'adi': 'Zara Erkek Polo Yaka T-Shirt','marka': 'Zara',       'kat': 'Erkek Giyim',
         'fiyat': 449.90,  'magaza': m4, 'stok': 9,  'min': 3,
         'ozellikler': [('Beyaz','S','Pamuk',0),('Lacivert','M','Pamuk',0),('Bordo','L','Pamuk',0),('Gri','XL','Pamuk',0)]},

        {'adi': 'Zara Yün Palto',              'marka': 'Zara',       'kat': 'Kadın Giyim',
         'fiyat': 2499.90, 'magaza': m4, 'stok': 4,  'min': 2,
         'ozellikler': [('Bej','XS','Yün',0),('Siyah','S','Yün',0),('Lacivert','M','Yün',0)]},

        {'adi': 'Zara Kadın Şort',             'marka': 'Zara',       'kat': 'Kadın Giyim',
         'fiyat': 349.90,  'magaza': m4, 'stok': 7,  'min': 3,
         'ozellikler': [('Beyaz','XS','Denim',0),('Lacivert','S','Denim',0),('Siyah','M','Denim',0)]},

        {'adi': 'Zara Erkek Spor Yelek',       'marka': 'Zara',       'kat': 'Erkek Giyim',
         'fiyat': 599.90,  'magaza': m4, 'stok': 2,  'min': 3,
         'ozellikler': [('Siyah','M','Polyester',0),('Lacivert','L','Polyester',0),('Gri','XL','Polyester',0)]},
    ]

    # ─── KOTON (m5) — 14 ürün ──────────────────────────────────────────────────
    koton = [
        {'adi': 'Koton Basic Kadın Tişört',    'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 149.90,  'magaza': m5, 'stok': 30, 'min': 8,
         'ozellikler': [('Beyaz','XS','Pamuk',0),('Siyah','S','Pamuk',0),('Kırmızı','M','Pamuk',0),('Lacivert','L','Pamuk',0),('Gri','XL','Pamuk',0)]},

        {'adi': 'Koton Erkek Spor Eşofman',    'marka': 'Koton',      'kat': 'Erkek Giyim',
         'fiyat': 449.90,  'magaza': m5, 'stok': 0,  'min': 5,
         'ozellikler': [('Siyah','M','Polyester',0),('Gri','L','Polyester',0),('Lacivert','XL','Polyester',0),('Bordo','XXL','Polyester',0)]},

        {'adi': 'Koton Viskon Maxi Elbise',    'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 399.90,  'magaza': m5, 'stok': 8,  'min': 3,
         'ozellikler': [('Lacivert','S','Viskon',0),('Yeşil','M','Viskon',0),('Bordo','L','Viskon',0)]},

        {'adi': 'Koton Triko Hırka',           'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 329.90,  'magaza': m5, 'stok': 5,  'min': 3,
         'ozellikler': [('Krem','XS','Triko',0),('Bej','S','Triko',0),('Pembe','M','Triko',0),('Gri','L','Triko',0)]},

        {'adi': 'Koton Çocuk Keten Şort',      'marka': 'Koton',      'kat': 'Çocuk Giyim',
         'fiyat': 99.90,   'magaza': m5, 'stok': 15, 'min': 5,
         'ozellikler': [('Bej','4-5 Yaş','Keten',0),('Beyaz','6-7 Yaş','Keten',0),('Mavi','8-9 Yaş','Keten',0),('Turuncu','10-11 Yaş','Keten',0)]},

        {'adi': 'Koton Erkek Polo Gömlek',     'marka': 'Koton',      'kat': 'Erkek Giyim',
         'fiyat': 249.90,  'magaza': m5, 'stok': 12, 'min': 4,
         'ozellikler': [('Beyaz','S','Pamuk',0),('Lacivert','M','Pamuk',0),('Kırmızı','L','Pamuk',0),('Gri','XL','Pamuk',0),('Bordo','XXL','Pamuk',0)]},

        {'adi': 'Koton Denim Mom Jean',        'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 499.90,  'magaza': m5, 'stok': 4,  'min': 3,
         'ozellikler': [('Lacivert','28','Denim',0),('Gri','30','Denim',0),('Siyah','32','Denim',0),('Açık Mavi','34','Denim',0)]},

        {'adi': 'Koton Yün Atkı',              'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 149.90,  'magaza': m5, 'stok': 20, 'min': 6,
         'ozellikler': [('Krem',None,'Yün',0),('Gri',None,'Yün',0),('Lacivert',None,'Yün',0),('Bordo',None,'Yün',0)]},

        {'adi': 'Koton Erkek Denim Şort',      'marka': 'Koton',      'kat': 'Erkek Giyim',
         'fiyat': 299.90,  'magaza': m5, 'stok': 0,  'min': 4,
         'ozellikler': [('Lacivert','30','Denim',0),('Gri','32','Denim',0),('Siyah','34','Denim',0)]},

        {'adi': 'Koton Şifon Bluz',            'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 179.90,  'magaza': m5, 'stok': 9,  'min': 3,
         'ozellikler': [('Beyaz','XS','Şifon',0),('Pembe','S','Şifon',0),('Lacivert','M','Şifon',0),('Yeşil','L','Şifon',0)]},

        {'adi': 'Koton Çocuk Sweatshirt',      'marka': 'Koton',      'kat': 'Çocuk Giyim',
         'fiyat': 169.90,  'magaza': m5, 'stok': 16, 'min': 5,
         'ozellikler': [('Gri','4-5 Yaş','Pamuk',0),('Kırmızı','6-7 Yaş','Pamuk',0),('Turuncu','8-9 Yaş','Pamuk',0),('Mavi','10-11 Yaş','Pamuk',0)]},

        {'adi': 'Koton Saten Ceket',           'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 649.90,  'magaza': m5, 'stok': 3,  'min': 2,
         'ozellikler': [('Siyah','XS','Saten',0),('Krem','S','Saten',0),('Yeşil','M','Saten',0)]},

        {'adi': 'Koton Kadife Pantolon',       'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 449.90,  'magaza': m5, 'stok': 6,  'min': 3,
         'ozellikler': [('Bordo','XS','Kadife',0),('Lacivert','S','Kadife',0),('Siyah','M','Kadife',0),('Kahverengi','L','Kadife',0)]},

        {'adi': 'Koton İpek Elbise',           'marka': 'Koton',      'kat': 'Kadın Giyim',
         'fiyat': 899.90,  'magaza': m5, 'stok': 0,  'min': 2,
         'ozellikler': [('Krem','XS','İpek',0),('Pembe','S','İpek',0),('Lacivert','M','İpek',0)]},
    ]

    urun_map = {}
    for grup in [lcw, tek, aya, zara, koton]:
        for d in grup:
            u = _ekle_urun(d, marka_map, kategori_map)
            urun_map[d['adi']] = u

    db.session.commit()
    toplam = sum(len(g) for g in [lcw, tek, aya, zara, koton])
    print(f"[+] {toplam} ürün ve stok girişi oluşturuldu.")
    return urun_map


def kampanyalar_olustur(urun_map, magazalar):
    m1, m2, m3, m4, m5 = magazalar
    bugun = datetime.utcnow()

    kampanyalar = [
        Kampanya(urun_id=urun_map['Kadın Yazlık Elbise'].id,       magaza_id=m1.id,
                 indirim_orani=20, baslangic_tarihi=bugun - timedelta(days=2), bitis_tarihi=bugun + timedelta(days=5)),
        Kampanya(urun_id=urun_map['Nike Air Max 90'].id,            magaza_id=m3.id,
                 indirim_orani=15, baslangic_tarihi=bugun,          bitis_tarihi=bugun + timedelta(days=7)),
        Kampanya(urun_id=urun_map['Erkek Slim Fit Jean'].id,        magaza_id=m1.id,
                 indirim_orani=30, baslangic_tarihi=bugun - timedelta(days=1), bitis_tarihi=bugun + timedelta(days=4)),
        Kampanya(urun_id=urun_map['Zara Viskon Midi Elbise'].id,    magaza_id=m4.id,
                 indirim_orani=25, baslangic_tarihi=bugun,          bitis_tarihi=bugun + timedelta(days=10)),
        Kampanya(urun_id=urun_map['Apple iPhone 15'].id,            magaza_id=m2.id,
                 indirim_orani=10, baslangic_tarihi=bugun - timedelta(days=3), bitis_tarihi=bugun + timedelta(days=3)),
        Kampanya(urun_id=urun_map['Adidas Ultraboost 22'].id,       magaza_id=m3.id,
                 indirim_orani=20, baslangic_tarihi=bugun,          bitis_tarihi=bugun + timedelta(days=6)),
        Kampanya(urun_id=urun_map['Koton Basic Kadın Tişört'].id,   magaza_id=m5.id,
                 indirim_orani=35, baslangic_tarihi=bugun - timedelta(days=1), bitis_tarihi=bugun + timedelta(days=8)),
        Kampanya(urun_id=urun_map['Zara İpek Bluz'].id,             magaza_id=m4.id,
                 indirim_orani=15, baslangic_tarihi=bugun,          bitis_tarihi=bugun + timedelta(days=5)),
    ]
    db.session.add_all(kampanyalar)
    db.session.commit()
    print("[+] 8 kampanya oluşturuldu.")


def benzer_urunler_olustur():
    """GÖREV 7: Aynı kategorideki ürünleri birbirine benzer olarak eşle."""
    from collections import defaultdict
    urunler = Urun.query.filter_by(aktif_mi=True).all()
    kat_gruplari = defaultdict(list)
    for u in urunler:
        kat_gruplari[u.kategori_id].append(u)

    kayit_sayisi = 0
    for kat_id, grup in kat_gruplari.items():
        if len(grup) < 2:
            continue
        for i, urun in enumerate(grup):
            benzerler = [u for u in grup if u.id != urun.id][:3]
            for b in benzerler:
                var = BenzerUrun.query.filter_by(urun_id=urun.id, benzer_urun_id=b.id).first()
                if not var:
                    db.session.add(BenzerUrun(urun_id=urun.id, benzer_urun_id=b.id))
                    kayit_sayisi += 1
    db.session.commit()
    print(f"[+] {kayit_sayisi} benzer ürün eşleşmesi oluşturuldu.")


def main():
    print("\n=== AKİS Seed Data ===\n")
    with app.app_context():
        temizle()
        roller_olustur()
        kullanici_map = kullanicilar_olustur()
        magazalar = magazalar_olustur(kullanici_map)
        kategori_map = kategoriler_olustur()
        marka_map = markalar_olustur()
        urun_map = urunler_ve_stoklar_olustur(magazalar, kategori_map, marka_map)
        kampanyalar_olustur(urun_map, magazalar)
        benzer_urunler_olustur()

        print("\n=== Seed tamamlandı! ===")
        print("\nGiriş bilgileri:")
        print("  Admin            : admin@avm.com        / a")
        print("  Sorumlu 1 (LC W) : sorumlu1@avm.com     / a")
        print("  Sorumlu 2 (Tek)  : sorumlu2@avm.com     / a")
        print("  Sorumlu 3 (Aya)  : sorumlu3@avm.com     / a")
        print("  Sorumlu 4 (Zara) : sorumlu4@avm.com     / a")
        print("  Sorumlu 5 (Koton): sorumlu5@avm.com     / a")
        print("  Müşteri          : musteri1@mail.com     / a")
        print("  Kiosk Terminal   : kiosk@avm.com         / a\n")


if __name__ == '__main__':
    main()
