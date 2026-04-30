"""
seed.py — AKİS Projesi Örnek Veri Doldurma Script'i

Kullanım:
    python seed.py

Oluşturulan veriler:
- 3 Rol (Müşteri, Mağaza Sorumlusu, Admin)
- 1 Admin, 3 Mağaza Sorumlusu, 2 Müşteri
- 3 Mağaza (her birine bir sorumlu)
- Kategori ağacı (Giyim, Elektronik, Ayakkabı ve alt kategoriler)
- 6 Marka
- Her mağazada 4-5 ürün ve stok girişi
- 2 Aktif kampanya
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Proje kök dizinini Python path'ine ekle
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

app = create_app('development')

def temizle():
    """Mevcut test verilerini sil."""
    BildirimTalebi.query.delete()
    Kampanya.query.delete()
    Stok.query.delete()
    UrunOzelligi.query.delete()
    Urun.query.delete()
    MagazaSorumlusu.query.delete()
    Magaza.query.delete()
    Kategori.query.delete()
    Marka.query.delete()
    Kullanici.query.delete()
    Rol.query.delete()
    db.session.commit()
    print("[*] Mevcut veriler temizlendi.")

def roller_olustur():
    roller = [
        Rol(id=1, rol_adi='Müşteri',          aciklama='AVM ziyaretçisi / alışverişçi'),
        Rol(id=2, rol_adi='Mağaza Sorumlusu', aciklama='Mağaza stok ve ürün yöneticisi'),
        Rol(id=3, rol_adi='Admin',             aciklama='Sistem yöneticisi'),
    ]
    db.session.add_all(roller)
    db.session.commit()
    print("[+] Roller oluşturuldu.")
    return {r.id: r for r in roller}

def kullanicilar_olustur():
    kullanicilar = [
        # Admin
        Kullanici(eposta='admin@avm.com',   sifre_hash=generate_password_hash('Admin1234!'),
                  ad='Sistem',   soyad='Yöneticisi', rol_id=3),
        # Mağaza Sorumluları
        Kullanici(eposta='sorumlu1@avm.com', sifre_hash=generate_password_hash('Sorumlu123!'),
                  ad='Ahmet',    soyad='Yılmaz',     rol_id=2),
        Kullanici(eposta='sorumlu2@avm.com', sifre_hash=generate_password_hash('Sorumlu123!'),
                  ad='Ayşe',     soyad='Kaya',       rol_id=2),
        Kullanici(eposta='sorumlu3@avm.com', sifre_hash=generate_password_hash('Sorumlu123!'),
                  ad='Mehmet',   soyad='Demir',      rol_id=2),
        # Müşteriler
        Kullanici(eposta='musteri1@mail.com', sifre_hash=generate_password_hash('Musteri123!'),
                  ad='Fatma',    soyad='Çelik',      rol_id=1),
        Kullanici(eposta='musteri2@mail.com', sifre_hash=generate_password_hash('Musteri123!'),
                  ad='Ali',      soyad='Şahin',      rol_id=1),
    ]
    db.session.add_all(kullanicilar)
    db.session.commit()
    print("[+] Kullanıcılar oluşturuldu.")
    kullanici_map = {k.eposta: k for k in kullanicilar}
    return kullanici_map

def magazalar_olustur(kullanici_map):
    magazalar = [
        Magaza(magaza_adi='LC Waikiki',  kat='1', konum_kodu='A-101',
               calisma_saati_baslangic='10:00', calisma_saati_bitis='22:00',
               aciklama='Giyim ve aksesuar mağazası'),
        Magaza(magaza_adi='Teknoloji Dünyası', kat='2', konum_kodu='B-210',
               calisma_saati_baslangic='10:00', calisma_saati_bitis='22:00',
               aciklama='Elektronik ve teknoloji ürünleri'),
        Magaza(magaza_adi='Ayakkabı Center',   kat='0', konum_kodu='Z-001',
               calisma_saati_baslangic='10:00', calisma_saati_bitis='21:30',
               aciklama='Her marka ayakkabı ve çanta'),
    ]
    db.session.add_all(magazalar)
    db.session.commit()
    print("[+] Mağazalar oluşturuldu.")

    # Sorumlu atamaları
    atamalar = [
        MagazaSorumlusu(magaza_id=magazalar[0].id, kullanici_id=kullanici_map['sorumlu1@avm.com'].id),
        MagazaSorumlusu(magaza_id=magazalar[1].id, kullanici_id=kullanici_map['sorumlu2@avm.com'].id),
        MagazaSorumlusu(magaza_id=magazalar[2].id, kullanici_id=kullanici_map['sorumlu3@avm.com'].id),
    ]
    db.session.add_all(atamalar)
    db.session.commit()
    print("[+] Mağaza sorumlu atamaları yapıldı.")
    return magazalar

def kategoriler_olustur():
    # Üst kategoriler
    giyim    = Kategori(kategori_adi='Giyim')
    elektro  = Kategori(kategori_adi='Elektronik')
    ayakkabi = Kategori(kategori_adi='Ayakkabı & Çanta')
    db.session.add_all([giyim, elektro, ayakkabi])
    db.session.flush()

    # Alt kategoriler
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
    marka_adlari = ['LC Waikiki', 'Zara', 'H&M', 'Koton', 'Mavi', 'Samsung', 'Apple', 'Nike', 'Adidas', 'Puma']
    markalar_list = [Marka(marka_adi=ad) for ad in marka_adlari]
    db.session.add_all(markalar_list)
    db.session.commit()
    print("[+] Markalar oluşturuldu.")
    return {m.marka_adi: m for m in markalar_list}

def urunler_ve_stoklar_olustur(magazalar, kategori_map, marka_map):
    m1, m2, m3 = magazalar[0], magazalar[1], magazalar[2]

    urunler_data = [
        # Mağaza 1 — LC Waikiki (Giyim)
        {'adi': 'Erkek Basic T-Shirt',    'marka': 'LC Waikiki', 'kat': 'Erkek Giyim',    'fiyat': 99.90,  'magaza': m1, 'stok': 25, 'min': 5,
         'ozellikler': [('Beyaz','S','Pamuk',0), ('Beyaz','M','Pamuk',0), ('Siyah','M','Pamuk',0), ('Siyah','L','Pamuk',0)]},
        {'adi': 'Kadın Yazlık Elbise',    'marka': 'LC Waikiki', 'kat': 'Kadın Giyim',    'fiyat': 249.90, 'magaza': m1, 'stok': 12, 'min': 3,
         'ozellikler': [('Lacivert','S','Viskon',0), ('Lacivert','M','Viskon',0), ('Çiçekli','M','Viskon',15)]},
        {'adi': 'Çocuk Eşofman Takımı',   'marka': 'LC Waikiki', 'kat': 'Çocuk Giyim',    'fiyat': 179.90, 'magaza': m1, 'stok': 8,  'min': 5,
         'ozellikler': [('Mavi','4-5 Yaş','Pamuk',0), ('Gri','6-7 Yaş','Pamuk',0)]},
        {'adi': 'Erkek Slim Fit Jean',    'marka': 'Mavi',       'kat': 'Erkek Giyim',    'fiyat': 399.90, 'magaza': m1, 'stok': 0,  'min': 5,
         'ozellikler': [('İndigo','28','Denim',0), ('İndigo','30','Denim',0), ('Siyah','30','Denim',0)]},
        {'adi': 'Kadın Keten Gömlek',     'marka': 'Koton',      'kat': 'Kadın Giyim',    'fiyat': 219.90, 'magaza': m1, 'stok': 15, 'min': 4,
         'ozellikler': [('Krem','XS','Keten',0), ('Krem','S','Keten',0), ('Bej','M','Keten',10)]},

        # Mağaza 2 — Teknoloji Dünyası (Elektronik)
        {'adi': 'Samsung Galaxy A55',      'marka': 'Samsung',    'kat': 'Telefon',         'fiyat': 14999.00, 'magaza': m2, 'stok': 7, 'min': 2,
         'ozellikler': [('Siyah',None,None,0), ('Beyaz',None,None,0), ('Lacivert',None,None,500)]},
        {'adi': 'Apple iPhone 15',         'marka': 'Apple',      'kat': 'Telefon',         'fiyat': 39999.00, 'magaza': m2, 'stok': 3, 'min': 2,
         'ozellikler': [('Siyah',None,None,0), ('Gri',None,None,0)]},
        {'adi': 'Samsung USB-C Şarj Aleti','marka': 'Samsung',    'kat': 'Aksesuar',        'fiyat': 249.00,  'magaza': m2, 'stok': 30, 'min': 10,
         'ozellikler': []},
        {'adi': 'Bluetooth Kulaklık',      'marka': 'Samsung',    'kat': 'Aksesuar',        'fiyat': 1299.00, 'magaza': m2, 'stok': 2,  'min': 3,
         'ozellikler': [('Siyah',None,None,0), ('Beyaz',None,None,0)]},

        # Mağaza 3 — Ayakkabı Center
        {'adi': 'Nike Air Max 90',         'marka': 'Nike',       'kat': 'Spor Ayakkabı',   'fiyat': 3499.00, 'magaza': m3, 'stok': 10, 'min': 3,
         'ozellikler': [('Beyaz','38',None,0), ('Beyaz','39',None,0), ('Siyah','40',None,0), ('Siyah','42',None,200)]},
        {'adi': 'Adidas Ultraboost 22',    'marka': 'Adidas',     'kat': 'Spor Ayakkabı',   'fiyat': 4299.00, 'magaza': m3, 'stok': 6,  'min': 3,
         'ozellikler': [('Siyah','39',None,0), ('Gri','40',None,0), ('Lacivert','41',None,0)]},
        {'adi': 'Puma Sneaker Kadın',      'marka': 'Puma',       'kat': 'Spor Ayakkabı',   'fiyat': 1799.00, 'magaza': m3, 'stok': 0,  'min': 4,
         'ozellikler': [('Pembe','36',None,0), ('Beyaz','37',None,0)]},
    ]

    urun_map = {}
    for d in urunler_data:
        urun = Urun(
            urun_adi=d['adi'],
            marka_id=marka_map[d['marka']].id,
            kategori_id=kategori_map[d['kat']].id,
            baz_fiyat=d['fiyat'],
        )
        db.session.add(urun)
        db.session.flush()

        # Özellikler
        for renk, beden, kumas, ek in d['ozellikler']:
            oz = UrunOzelligi(urun_id=urun.id, renk=renk, beden=beden, kumas_turu=kumas, ek_fiyat=ek)
            db.session.add(oz)

        # Stok
        stok = Stok(
            urun_id=urun.id,
            magaza_id=d['magaza'].id,
            stok_adedi=d['stok'],
            min_stok_seviyesi=d['min'],
            guncelleme_turu='Manuel',
        )
        db.session.add(stok)
        urun_map[d['adi']] = urun

    db.session.commit()
    print(f"[+] {len(urunler_data)} ürün ve stok girişi oluşturuldu.")
    return urun_map

def kampanyalar_olustur(urun_map, magazalar):
    bugun = datetime.utcnow()
    kampanyalar = [
        Kampanya(
            urun_id=urun_map['Kadın Yazlık Elbise'].id,
            magaza_id=magazalar[0].id,
            indirim_orani=20,
            baslangic_tarihi=bugun - timedelta(days=2),
            bitis_tarihi=bugun + timedelta(days=5),
        ),
        Kampanya(
            urun_id=urun_map['Nike Air Max 90'].id,
            magaza_id=magazalar[2].id,
            indirim_orani=15,
            baslangic_tarihi=bugun,
            bitis_tarihi=bugun + timedelta(days=7),
        ),
    ]
    db.session.add_all(kampanyalar)
    db.session.commit()
    print("[+] Kampanyalar oluşturuldu.")

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

        print("\n=== Seed tamamlandı! ===")
        print("\nGiriş bilgileri:")
        print("  Admin          : admin@avm.com        / Admin1234!")
        print("  Sorumlu 1 (LC W): sorumlu1@avm.com     / Sorumlu123!")
        print("  Sorumlu 2 (Tek) : sorumlu2@avm.com     / Sorumlu123!")
        print("  Sorumlu 3 (Aya) : sorumlu3@avm.com     / Sorumlu123!")
        print("  Müşteri        : musteri1@mail.com     / Musteri123!\n")

if __name__ == '__main__':
    main()
