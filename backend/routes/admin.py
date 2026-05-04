from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from werkzeug.security import generate_password_hash
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..models.kullanicilar import Kullanici
from ..models.magazalar import Magaza
from ..models.magaza_sorumlulari import MagazaSorumlusu
from ..models.kategoriler import Kategori
from ..models.markalar import Marka
from ..models.stoklar import Stok
from ..models.urunler import Urun
from ..models.kampanyalar import Kampanya
from ..models.urun_ozellikleri import UrunOzelligi
from ..models.arama_gecmisi import AramaGecmisi
from ..models.sync_log import SyncLog
from ..utils.decorators import role_required

admin_bp = Blueprint('admin', __name__)


# ─────────────────────────────────────────────────────────── DASHBOARD ──

@admin_bp.route('/dashboard')
@login_required
@role_required(3)
def dashboard():
    aktif_magaza_sayisi = Magaza.query.filter_by(aktif_mi=True).count()
    toplam_kullanici = Kullanici.query.filter_by(aktif_mi=True).count()

    bugun_baslangic = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    bugun_arama = AramaGecmisi.query.filter(AramaGecmisi.tarih >= bugun_baslangic).count()

    sync_loglar = SyncLog.query.order_by(SyncLog.tarih.desc()).limit(20).all()
    basarisiz_sync_sayisi = SyncLog.query.filter_by(cozuldu_mu=False).count()

    gun_adlari_kisa = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
    gun_adlari_tam = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    today = datetime.now().date()
    isi_haritasi_verisi = []
    isi_maks = 1
    for i in range(6, -1, -1):
        gun = today - timedelta(days=i)
        gun_dt = datetime(gun.year, gun.month, gun.day)
        gun_verisi = {
            'gun_kisa': gun_adlari_kisa[gun.weekday()],
            'gun_tam': gun_adlari_tam[gun.weekday()],
            'saatler': []
        }
        for saat in range(24):
            bas = gun_dt + timedelta(hours=saat)
            bitis = bas + timedelta(hours=1)
            sayi = AramaGecmisi.query.filter(
                AramaGecmisi.tarih >= bas, AramaGecmisi.tarih < bitis
            ).count()
            gun_verisi['saatler'].append({'saat': saat, 'sayi': sayi})
            if sayi > isi_maks:
                isi_maks = sayi
        isi_haritasi_verisi.append(gun_verisi)

    return render_template('admin/dashboard.html',
                           aktif_magaza_sayisi=aktif_magaza_sayisi,
                           toplam_kullanici=toplam_kullanici,
                           bugun_arama=bugun_arama,
                           basarisiz_sync_sayisi=basarisiz_sync_sayisi,
                           isi_haritasi_verisi=isi_haritasi_verisi,
                           isi_maks=isi_maks,
                           sync_loglar=sync_loglar)


# ─────────────────────────────────────────────────────────── STORES ──

@admin_bp.route('/stores', methods=['GET', 'POST'])
@login_required
@role_required(3)
def stores():
    if request.method == 'POST':
        try:
            magaza = Magaza(
                magaza_adi=request.form.get('magaza_adi', '').strip(),
                kat=request.form.get('kat', '').strip(),
                konum_kodu=request.form.get('konum_kodu', '').strip().upper(),
                calisma_saati_baslangic=request.form.get('calisma_saati_baslangic'),
                calisma_saati_bitis=request.form.get('calisma_saati_bitis'),
                aciklama=request.form.get('aciklama', '').strip() or None,
            )
            db.session.add(magaza)
            db.session.flush()
            sorumlu_id = request.form.get('sorumlu_id', type=int)
            if sorumlu_id:
                atama = MagazaSorumlusu(magaza_id=magaza.id, kullanici_id=sorumlu_id)
                db.session.add(atama)
            db.session.commit()
            flash('Mağaza başarıyla eklendi.', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Bu konum kodu zaten kullanılıyor (BR-4.1).', 'danger')
    magazalar = Magaza.query.order_by(Magaza.aktif_mi.desc(), Magaza.magaza_adi).all()
    sorumlular = Kullanici.query.filter_by(rol_id=2, aktif_mi=True).all()
    return render_template('admin/stores.html', magazalar=magazalar, sorumlular=sorumlular)


@admin_bp.route('/stores/<int:magaza_id>/update', methods=['POST'])
@login_required
@role_required(3)
def update_store(magaza_id):
    magaza = Magaza.query.get_or_404(magaza_id)
    magaza.magaza_adi = request.form.get('magaza_adi', magaza.magaza_adi).strip()
    magaza.kat = request.form.get('kat', magaza.kat).strip()
    magaza.calisma_saati_baslangic = request.form.get('calisma_saati_baslangic', magaza.calisma_saati_baslangic)
    magaza.calisma_saati_bitis = request.form.get('calisma_saati_bitis', magaza.calisma_saati_bitis)
    aciklama = request.form.get('aciklama', '').strip()
    magaza.aciklama = aciklama or magaza.aciklama
    db.session.commit()
    flash(f'"{magaza.magaza_adi}" mağazası güncellendi.', 'success')
    return redirect(url_for('admin.stores'))


@admin_bp.route('/stores/<int:magaza_id>/assign', methods=['POST'])
@login_required
@role_required(3)
def assign_manager(magaza_id):
    kullanici_id = request.form.get('kullanici_id', type=int)
    if kullanici_id:
        mevcut = MagazaSorumlusu.query.filter_by(magaza_id=magaza_id, kullanici_id=kullanici_id).first()
        if not mevcut:
            atama = MagazaSorumlusu(magaza_id=magaza_id, kullanici_id=kullanici_id)
            db.session.add(atama)
            db.session.commit()
            flash('Sorumlu başarıyla atandı.', 'success')
        else:
            flash('Bu kullanıcı zaten bu mağazaya atanmış.', 'warning')
    return redirect(url_for('admin.stores'))


@admin_bp.route('/stores/<int:magaza_id>/deactivate', methods=['POST'])
@login_required
@role_required(3)
def deactivate_store(magaza_id):
    magaza = Magaza.query.get_or_404(magaza_id)
    magaza.aktif_mi = False
    db.session.commit()
    flash('Mağaza pasif hale getirildi.', 'success')
    return redirect(url_for('admin.stores'))


@admin_bp.route('/stores/<int:magaza_id>/activate', methods=['POST'])
@login_required
@role_required(3)
def activate_store(magaza_id):
    magaza = Magaza.query.get_or_404(magaza_id)
    magaza.aktif_mi = True
    db.session.commit()
    flash('Mağaza aktif edildi.', 'success')
    return redirect(url_for('admin.stores'))


# ─────────────────────────────────────────────────────────── USERS ──

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@role_required(3)
def users():
    if request.method == 'POST':
        try:
            sifre = request.form.get('sifre', '')
            if len(sifre) < 8:
                flash('Şifre en az 8 karakter olmalıdır.', 'danger')
                magazalar = Magaza.query.filter_by(aktif_mi=True).all()
                kullanicilar = Kullanici.query.filter_by(aktif_mi=True).all()
                return render_template('admin/users.html', kullanicilar=kullanicilar, magazalar=magazalar)
            kullanici = Kullanici(
                eposta=request.form.get('eposta', '').strip(),
                sifre_hash=generate_password_hash(sifre),
                ad=request.form.get('ad', '').strip(),
                soyad=request.form.get('soyad', '').strip(),
                rol_id=request.form.get('rol_id', 1, type=int),
            )
            db.session.add(kullanici)
            db.session.flush()
            magaza_id = request.form.get('magaza_id', type=int)
            if kullanici.rol_id == 2 and magaza_id:
                atama = MagazaSorumlusu(magaza_id=magaza_id, kullanici_id=kullanici.id)
                db.session.add(atama)
            db.session.commit()
            flash('Kullanıcı başarıyla oluşturuldu.', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Bu e-posta adresi zaten kayıtlı.', 'danger')

    # GET: filter support
    q = request.args.get('q', '').strip()
    rol_id_filtre = request.args.get('rol_id', type=int)
    sorgu = Kullanici.query
    if q:
        sorgu = sorgu.filter(
            or_(Kullanici.ad.ilike(f'%{q}%'),
                Kullanici.soyad.ilike(f'%{q}%'),
                Kullanici.eposta.ilike(f'%{q}%'))
        )
    if rol_id_filtre:
        sorgu = sorgu.filter_by(rol_id=rol_id_filtre)
    kullanicilar = sorgu.order_by(Kullanici.aktif_mi.desc(), Kullanici.ad).all()
    magazalar = Magaza.query.filter_by(aktif_mi=True).order_by(Magaza.magaza_adi).all()
    return render_template('admin/users.html', kullanicilar=kullanicilar, magazalar=magazalar)


@admin_bp.route('/users/<int:kullanici_id>/role', methods=['POST'])
@login_required
@role_required(3)
def update_user_role(kullanici_id):
    kullanici = Kullanici.query.get_or_404(kullanici_id)
    yeni_rol = request.form.get('rol_id', type=int)
    if yeni_rol and yeni_rol in [1, 2, 3, 4]:
        kullanici.rol_id = yeni_rol
        magaza_id = request.form.get('magaza_id', type=int)
        if yeni_rol == 2 and magaza_id:
            mevcut = MagazaSorumlusu.query.filter_by(kullanici_id=kullanici_id, magaza_id=magaza_id).first()
            if not mevcut:
                db.session.add(MagazaSorumlusu(magaza_id=magaza_id, kullanici_id=kullanici_id))
        db.session.commit()
        flash(f'{kullanici.ad} {kullanici.soyad} rolü güncellendi.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:kullanici_id>/deactivate', methods=['POST'])
@login_required
@role_required(3)
def deactivate_user(kullanici_id):
    kullanici = Kullanici.query.get_or_404(kullanici_id)
    kullanici.aktif_mi = False
    db.session.commit()
    flash('Kullanıcı pasif yapıldı.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:kullanici_id>/activate', methods=['POST'])
@login_required
@role_required(3)
def activate_user(kullanici_id):
    kullanici = Kullanici.query.get_or_404(kullanici_id)
    kullanici.aktif_mi = True
    db.session.commit()
    flash('Kullanıcı aktif edildi.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:kullanici_id>/reset-password', methods=['POST'])
@login_required
@role_required(3)
def reset_password(kullanici_id):
    kullanici = Kullanici.query.get_or_404(kullanici_id)
    yeni_sifre = request.form.get('yeni_sifre', '')
    if len(yeni_sifre) < 8:
        flash('Şifre en az 8 karakter olmalıdır.', 'danger')
        return redirect(url_for('admin.users'))
    kullanici.sifre_hash = generate_password_hash(yeni_sifre)
    db.session.commit()
    flash(f'{kullanici.ad} {kullanici.soyad} şifresi sıfırlandı.', 'success')
    return redirect(url_for('admin.users'))


# ─────────────────────────────────────────────────────────── CATEGORIES ──

@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@role_required(3)
def categories():
    if request.method == 'POST':
        kategori_adi = request.form.get('kategori_adi', '').strip()
        if not kategori_adi:
            flash('Kategori adı boş olamaz.', 'danger')
        else:
            kategori = Kategori(
                kategori_adi=kategori_adi,
                ust_kategori_id=request.form.get('ust_kategori_id') or None
            )
            db.session.add(kategori)
            db.session.commit()
            flash(f'"{kategori_adi}" kategorisi eklendi.', 'success')
    kategoriler = Kategori.query.order_by(Kategori.ust_kategori_id.nullsfirst(), Kategori.kategori_adi).all()
    renkler = [r[0] for r in db.session.query(UrunOzelligi.renk).distinct().filter(UrunOzelligi.renk.isnot(None)).all()]
    bedenler = [b[0] for b in db.session.query(UrunOzelligi.beden).distinct().filter(UrunOzelligi.beden.isnot(None)).all()]
    kumaslar = [k[0] for k in db.session.query(UrunOzelligi.kumas_turu).distinct().filter(UrunOzelligi.kumas_turu.isnot(None)).all()]
    return render_template('admin/categories.html', kategoriler=kategoriler,
                           renkler=renkler, bedenler=bedenler, kumaslar=kumaslar)


@admin_bp.route('/categories/<int:kategori_id>/update', methods=['POST'])
@login_required
@role_required(3)
def update_category(kategori_id):
    kategori = Kategori.query.get_or_404(kategori_id)
    yeni_ad = request.form.get('kategori_adi', '').strip()
    if yeni_ad:
        kategori.kategori_adi = yeni_ad
        db.session.commit()
        flash(f'Kategori "{yeni_ad}" olarak güncellendi.', 'success')
    else:
        flash('Kategori adı boş olamaz.', 'danger')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/<int:kategori_id>/delete', methods=['POST'])
@login_required
@role_required(3)
def delete_category(kategori_id):
    kategori = Kategori.query.get_or_404(kategori_id)
    kategori.aktif_mi = False
    db.session.commit()
    flash('Kategori pasif yapıldı.', 'success')
    return redirect(url_for('admin.categories'))


# ─────────────────────────────────────────────────────────── BRANDS ──

@admin_bp.route('/brands', methods=['GET', 'POST'])
@login_required
@role_required(3)
def brands():
    if request.method == 'POST':
        marka_adi = request.form.get('marka_adi', '').strip()
        if not marka_adi:
            flash('Marka adı boş olamaz.', 'danger')
        elif Marka.query.filter_by(marka_adi=marka_adi).first():
            flash('Bu marka adı zaten mevcut.', 'warning')
        else:
            marka = Marka(marka_adi=marka_adi)
            db.session.add(marka)
            db.session.commit()
            flash(f'"{marka_adi}" markası eklendi.', 'success')
    markalar = Marka.query.order_by(Marka.aktif_mi.desc(), Marka.marka_adi).all()
    return render_template('admin/brands.html', markalar=markalar)


@admin_bp.route('/brands/<int:marka_id>/deactivate', methods=['POST'])
@login_required
@role_required(3)
def deactivate_brand(marka_id):
    marka = Marka.query.get_or_404(marka_id)
    marka.aktif_mi = False
    db.session.commit()
    flash(f'"{marka.marka_adi}" markası pasif yapıldı.', 'success')
    return redirect(url_for('admin.brands'))


@admin_bp.route('/brands/<int:marka_id>/activate', methods=['POST'])
@login_required
@role_required(3)
def activate_brand(marka_id):
    marka = Marka.query.get_or_404(marka_id)
    marka.aktif_mi = True
    db.session.commit()
    flash(f'"{marka.marka_adi}" markası aktif edildi.', 'success')
    return redirect(url_for('admin.brands'))


# ─────────────────────────────────────────────────────────── REPORTS ──

@admin_bp.route('/reports')
@login_required
@role_required(3)
def reports():
    magaza_sayisi = Magaza.query.filter_by(aktif_mi=True).count()
    kullanici_sayisi = Kullanici.query.filter_by(aktif_mi=True).count()
    toplam_urun_sayisi = Urun.query.filter_by(aktif_mi=True).count()
    toplam_kampanya_sayisi = Kampanya.query.filter_by(aktif_mi=True).filter(
        Kampanya.bitis_tarihi >= datetime.now()
    ).count()
    dusuk_stoklar = Stok.query.filter(Stok.stok_adedi <= Stok.min_stok_seviyesi).all()

    magazalar = Magaza.query.filter_by(aktif_mi=True).all()
    magaza_ozet = []
    for m in magazalar:
        urun_sayisi = Stok.query.filter_by(magaza_id=m.id).count()
        kampanya_sayisi = Kampanya.query.filter_by(
            magaza_id=m.id, aktif_mi=True
        ).filter(Kampanya.bitis_tarihi >= datetime.now()).count()
        magaza_ozet.append({
            'magaza_adi': m.magaza_adi,
            'kat': m.kat,
            'konum_kodu': m.konum_kodu,
            'urun_sayisi': urun_sayisi,
            'kampanya_sayisi': kampanya_sayisi,
        })

    populer_magazalar = sorted(magaza_ozet, key=lambda x: x['urun_sayisi'], reverse=True)[:5]

    kategori_sorgu = (db.session.query(Kategori.kategori_adi, func.count(Urun.id))
                      .join(Urun, Urun.kategori_id == Kategori.id)
                      .filter(Urun.aktif_mi == True)
                      .group_by(Kategori.kategori_adi)
                      .order_by(func.count(Urun.id).desc()).all())
    kategori_dagilimi = [{'kategori_adi': r[0], 'urun_sayisi': r[1]} for r in kategori_sorgu]

    en_cok_arama = (db.session.query(AramaGecmisi.arama_metni, func.count(AramaGecmisi.id).label('sayi'))
                    .group_by(AramaGecmisi.arama_metni)
                    .order_by(func.count(AramaGecmisi.id).desc())
                    .limit(10).all())
    en_cok_aranan = [{'kelime': r[0], 'sayi': r[1]} for r in en_cok_arama]

    today = datetime.now().date()
    son_7_gun_arama = []
    for i in range(6, -1, -1):
        gun = today - timedelta(days=i)
        gun_baslangic = datetime(gun.year, gun.month, gun.day)
        gun_bitis = gun_baslangic + timedelta(days=1)
        sayi = AramaGecmisi.query.filter(
            AramaGecmisi.tarih >= gun_baslangic,
            AramaGecmisi.tarih < gun_bitis
        ).count()
        son_7_gun_arama.append({'gun': gun.strftime('%d.%m'), 'sayi': sayi})

    chart_labels = [m['magaza_adi'] for m in magaza_ozet]
    chart_urun = [m['urun_sayisi'] for m in magaza_ozet]
    chart_kampanya = [m['kampanya_sayisi'] for m in magaza_ozet]
    chart_kategori_labels = [k['kategori_adi'] for k in kategori_dagilimi]
    chart_kategori_data = [k['urun_sayisi'] for k in kategori_dagilimi]
    chart_arama_gun = [d['gun'] for d in son_7_gun_arama]
    chart_arama_sayi = [d['sayi'] for d in son_7_gun_arama]

    return render_template('admin/reports.html',
                           magaza_sayisi=magaza_sayisi,
                           kullanici_sayisi=kullanici_sayisi,
                           toplam_urun_sayisi=toplam_urun_sayisi,
                           toplam_kampanya_sayisi=toplam_kampanya_sayisi,
                           dusuk_stoklar=dusuk_stoklar,
                           magaza_ozet=magaza_ozet,
                           populer_magazalar=populer_magazalar,
                           kategori_dagilimi=kategori_dagilimi,
                           en_cok_aranan=en_cok_aranan,
                           son_7_gun_arama=son_7_gun_arama,
                           chart_labels=chart_labels,
                           chart_urun=chart_urun,
                           chart_kampanya=chart_kampanya,
                           chart_kategori_labels=chart_kategori_labels,
                           chart_kategori_data=chart_kategori_data,
                           chart_arama_gun=chart_arama_gun,
                           chart_arama_sayi=chart_arama_sayi)
