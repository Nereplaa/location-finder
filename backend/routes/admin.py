from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from werkzeug.security import generate_password_hash
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
from ..utils.decorators import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@role_required(3)
def dashboard():
    aktif_magaza_sayisi = Magaza.query.filter_by(aktif_mi=True).count()
    toplam_kullanici = Kullanici.query.filter_by(aktif_mi=True).count()
    return render_template('admin/dashboard.html',
                           aktif_magaza_sayisi=aktif_magaza_sayisi,
                           toplam_kullanici=toplam_kullanici,
                           bugun_arama=0,
                           basarisiz_sync_sayisi=0,
                           isi_haritasi_verisi=[],
                           sync_loglar=[])

@admin_bp.route('/stores', methods=['GET', 'POST'])
@login_required
@role_required(3)
def stores():
    if request.method == 'POST':
        try:
            magaza = Magaza(
                magaza_adi=request.form.get('magaza_adi'),
                kat=request.form.get('kat'),
                konum_kodu=request.form.get('konum_kodu'),
                calisma_saati_baslangic=request.form.get('calisma_saati_baslangic'),
                calisma_saati_bitis=request.form.get('calisma_saati_bitis')
            )
            db.session.add(magaza)
            db.session.commit()
            # Sorumlu atama (FR-3.1)
            sorumlu_id = request.form.get('sorumlu_id', type=int)
            if sorumlu_id:
                atama = MagazaSorumlusu(magaza_id=magaza.id, kullanici_id=sorumlu_id)
                db.session.add(atama)
                db.session.commit()
            flash('Mağaza başarıyla eklendi.', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Bu konum kodu zaten kullanılıyor.', 'danger')
    magazalar = Magaza.query.filter_by(aktif_mi=True).all()
    # Sorumlu olarak atanabilecek kullanıcılar (rol_id=2)
    sorumlular = Kullanici.query.filter_by(rol_id=2, aktif_mi=True).all()
    return render_template('admin/stores.html', magazalar=magazalar, sorumlular=sorumlular)


@admin_bp.route('/stores/<int:magaza_id>/assign', methods=['POST'])
@login_required
@role_required(3)
def assign_manager(magaza_id):
    """FR-3.1: Mağazaya sorumlu ata."""
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

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@role_required(3)
def users():
    if request.method == 'POST':
        try:
            kullanici = Kullanici(
                eposta=request.form.get('eposta'),
                sifre_hash=generate_password_hash(request.form.get('sifre')),
                ad=request.form.get('ad'),
                soyad=request.form.get('soyad'),
                rol_id=request.form.get('rol_id', type=int)
            )
            db.session.add(kullanici)
            db.session.commit()
            flash('Kullanıcı başarıyla oluşturuldu.', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Bu e-posta adresi zaten kayıtlı.', 'danger')
    kullanicilar = Kullanici.query.filter_by(aktif_mi=True).all()
    return render_template('admin/users.html', kullanicilar=kullanicilar)

@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@role_required(3)
def categories():
    if request.method == 'POST':
        kategori = Kategori(
            kategori_adi=request.form.get('kategori_adi'),
            ust_kategori_id=request.form.get('ust_kategori_id') or None
        )
        db.session.add(kategori)
        db.session.commit()
        flash('Kategori eklendi.', 'success')
    kategoriler = Kategori.query.filter_by(aktif_mi=True).all()
    # FR-3.2: Parametre yönetimi — distinct renk, beden, kumaş listesi
    renkler = [r[0] for r in db.session.query(UrunOzelligi.renk).distinct().filter(UrunOzelligi.renk.isnot(None)).all()]
    bedenler = [b[0] for b in db.session.query(UrunOzelligi.beden).distinct().filter(UrunOzelligi.beden.isnot(None)).all()]
    kumaslar = [k[0] for k in db.session.query(UrunOzelligi.kumas_turu).distinct().filter(UrunOzelligi.kumas_turu.isnot(None)).all()]
    return render_template('admin/categories.html', kategoriler=kategoriler,
                           renkler=renkler, bedenler=bedenler, kumaslar=kumaslar)

@admin_bp.route('/reports')
@login_required
@role_required(3)
def reports():
    from datetime import datetime
    magaza_sayisi = Magaza.query.filter_by(aktif_mi=True).count()
    kullanici_sayisi = Kullanici.query.filter_by(aktif_mi=True).count()
    dusuk_stoklar = Stok.query.filter(Stok.stok_adedi <= Stok.min_stok_seviyesi).all()

    # Mağaza bazlı özet (Chart.js için)
    magazalar = Magaza.query.filter_by(aktif_mi=True).all()
    magaza_ozet = []
    for m in magazalar:
        urun_sayisi = Stok.query.filter_by(magaza_id=m.id).count()
        kampanya_sayisi = Kampanya.query.filter_by(
            magaza_id=m.id, aktif_mi=True
        ).filter(Kampanya.bitis_tarihi >= datetime.utcnow()).count()
        magaza_ozet.append({
            'magaza_adi': m.magaza_adi,
            'kat': m.kat,
            'konum_kodu': m.konum_kodu,
            'urun_sayisi': urun_sayisi,
            'kampanya_sayisi': kampanya_sayisi,
        })

    # Chart.js: mağaza adları ve ürün sayıları
    chart_labels = [m['magaza_adi'] for m in magaza_ozet]
    chart_urun = [m['urun_sayisi'] for m in magaza_ozet]
    chart_kampanya = [m['kampanya_sayisi'] for m in magaza_ozet]

    return render_template('admin/reports.html',
                           magaza_sayisi=magaza_sayisi,
                           kullanici_sayisi=kullanici_sayisi,
                           dusuk_stoklar=dusuk_stoklar,
                           magaza_ozet=magaza_ozet,
                           chart_labels=chart_labels,
                           chart_urun=chart_urun,
                           chart_kampanya=chart_kampanya)

@admin_bp.route('/stores/<int:magaza_id>/activate', methods=['POST'])
@login_required
@role_required(3)
def activate_store(magaza_id):
    magaza = Magaza.query.get_or_404(magaza_id)
    magaza.aktif_mi = True
    db.session.commit()
    flash('Mağaza aktif edildi.', 'success')
    return redirect(url_for('admin.stores'))

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
    flash('Şifre başarıyla sıfırlandı.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/categories/<int:kategori_id>/delete', methods=['POST'])
@login_required
@role_required(3)
def delete_category(kategori_id):
    kategori = Kategori.query.get_or_404(kategori_id)
    kategori.aktif_mi = False
    db.session.commit()
    flash('Kategori pasif yapıldı.', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/brands', methods=['GET', 'POST'])
@login_required
@role_required(3)
def brands():
    """FR-3.2: Marka yönetimi — ekleme ve listeleme."""
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
    markalar = Marka.query.order_by(Marka.marka_adi).all()
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
