from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..extensions import db
from ..models.urunler import Urun
from ..models.stoklar import Stok
from ..models.kampanyalar import Kampanya
from ..models.magaza_sorumlulari import MagazaSorumlusu
from ..models.magazalar import Magaza
from ..models.kategoriler import Kategori
from ..models.markalar import Marka
from ..utils.decorators import role_required
from ..services.stock_service import stok_guncelle

manager_bp = Blueprint('manager', __name__)

def get_sorumlu_magaza_id():
    """Giriş yapan sorumluya ait mağaza id'sini döner (BR-1.1)"""
    atama = MagazaSorumlusu.query.filter_by(kullanici_id=current_user.id).first()
    return atama.magaza_id if atama else None

@manager_bp.route('/dashboard')
@login_required
@role_required(2)
def dashboard():
    from datetime import datetime
    magaza_id = get_sorumlu_magaza_id()
    magaza = Magaza.query.get(magaza_id)
    dusuk_stoklar = Stok.query.filter_by(magaza_id=magaza_id).filter(
        Stok.stok_adedi <= Stok.min_stok_seviyesi
    ).all()
    tum_stoklar = Stok.query.filter_by(magaza_id=magaza_id).all()
    toplam_urun = len(tum_stoklar)
    aktif_kampanya_sayisi = Kampanya.query.filter_by(
        magaza_id=magaza_id, aktif_mi=True
    ).filter(Kampanya.bitis_tarihi >= datetime.utcnow()).count()
    markalar = Marka.query.filter_by(aktif_mi=True).all()
    kategoriler = Kategori.query.filter_by(aktif_mi=True).all()
    return render_template('manager/dashboard.html',
                           magaza=magaza,
                           dusuk_stoklar=dusuk_stoklar,
                           kritik_stoklar=dusuk_stoklar,
                           kritik_stok_sayisi=len(dusuk_stoklar),
                           toplam_urun=toplam_urun,
                           tum_stoklar=tum_stoklar,
                           aktif_kampanya_sayisi=aktif_kampanya_sayisi,
                           markalar=markalar,
                           kategoriler=kategoriler,
                           populer_urunler=[],
                           goruntuleme_istatistikleri=None,
                           bugun_goruntuleme=0)

@manager_bp.route('/products', methods=['GET', 'POST'])
@login_required
@role_required(2)
def products():
    magaza_id = get_sorumlu_magaza_id()
    if request.method == 'POST':
        urun_adi = request.form.get('urun_adi')
        marka_id = request.form.get('marka_id', type=int)
        kategori_id = request.form.get('kategori_id', type=int)
        baz_fiyat = request.form.get('baz_fiyat', type=float)
        aciklama = request.form.get('aciklama', '').strip() or None
        gorsel_url = request.form.get('gorsel_url', '').strip() or None
        stok_adedi = request.form.get('stok_adedi', 0, type=int)
        if stok_adedi < 0:
            stok_adedi = 0
        urun = Urun(urun_adi=urun_adi, marka_id=marka_id, kategori_id=kategori_id,
                    baz_fiyat=baz_fiyat, aciklama=aciklama, gorsel_url=gorsel_url)
        db.session.add(urun)
        db.session.flush()
        stok = Stok(urun_id=urun.id, magaza_id=magaza_id, stok_adedi=stok_adedi, guncelleme_turu='Manuel')
        db.session.add(stok)
        db.session.commit()
        flash('Ürün başarıyla eklendi.', 'success')
    stoklar = Stok.query.filter_by(magaza_id=magaza_id).join(Urun).filter(Urun.aktif_mi == True).all()
    # Template iterates over 'urunler' and accesses urun.stok (singular)
    # Build a list of Urun objects with a store-specific .stok attribute
    urunler = []
    for s in stoklar:
        urun = s.urun
        urun.stok = s  # attach store-specific stok
        urunler.append(urun)
    markalar = Marka.query.filter_by(aktif_mi=True).all()
    kategoriler = Kategori.query.filter_by(aktif_mi=True).all()
    return render_template('manager/products.html', urunler=urunler, stoklar=stoklar, markalar=markalar, kategoriler=kategoriler)

@manager_bp.route('/products/<int:urun_id>/stock', methods=['POST'])
@login_required
@role_required(2)
def update_stock(urun_id):
    magaza_id = get_sorumlu_magaza_id()
    yeni_adet = request.form.get('stok_adedi', type=int)
    stok_guncelle(urun_id, magaza_id, yeni_adet, 'Manuel', current_user.id)
    flash('Stok başarıyla güncellendi.', 'success')
    return redirect(url_for('manager.products'))

@manager_bp.route('/products/<int:urun_id>/deactivate', methods=['POST'])
@login_required
@role_required(2)
def deactivate_product(urun_id):
    magaza_id = get_sorumlu_magaza_id()
    # BR-1.1: Sahiplik kontrolü — ürün bu mağazaya ait mi?
    stok = Stok.query.filter_by(urun_id=urun_id, magaza_id=magaza_id).first()
    if not stok:
        flash('Bu ürün üzerinde yetkiniz yok.', 'danger')
        return redirect(url_for('manager.products')), 403
    urun = Urun.query.get_or_404(urun_id)
    urun.aktif_mi = False  # Soft delete (BR-2.4)
    db.session.commit()
    flash('Ürün pasif hale getirildi.', 'success')
    return redirect(url_for('manager.products'))

@manager_bp.route('/products/<int:urun_id>/reset-stock', methods=['POST'])
@login_required
@role_required(2)
def reset_stock(urun_id):
    magaza_id = get_sorumlu_magaza_id()
    # BR-1.1: Sahiplik kontrolü — stok bu mağazaya ait mi?
    stok = Stok.query.filter_by(urun_id=urun_id, magaza_id=magaza_id).first()
    if not stok:
        flash('Bu ürün üzerinde yetkiniz yok.', 'danger')
        return redirect(url_for('manager.products')), 403
    stok_guncelle(urun_id, magaza_id, 0, 'Manuel', current_user.id)  # BR-2.1
    flash('Stok sıfırlandı.', 'success')
    return redirect(url_for('manager.products'))

@manager_bp.route('/campaigns', methods=['GET', 'POST'])
@login_required
@role_required(2)
def campaigns():
    from datetime import datetime
    magaza_id = get_sorumlu_magaza_id()
    if request.method == 'POST':
        urun_id = request.form.get('urun_id', type=int)
        indirim = request.form.get('indirim_orani', type=float)
        baslangic_str = request.form.get('baslangic_tarihi', '')
        bitis_str = request.form.get('bitis_tarihi', '')
        try:
            # Support both date-only and datetime-local formats
            fmt = '%Y-%m-%dT%H:%M' if 'T' in baslangic_str else '%Y-%m-%d'
            baslangic = datetime.strptime(baslangic_str, fmt)
            bitis = datetime.strptime(bitis_str, '%Y-%m-%dT%H:%M' if 'T' in bitis_str else '%Y-%m-%d')
        except (ValueError, TypeError):
            flash('Geçersiz tarih formatı.', 'danger')
            baslangic = bitis = None
        if baslangic and bitis:
            if bitis <= baslangic:  # BR-3.1
                flash('Bitiş tarihi başlangıç tarihinden sonra olmalıdır.', 'danger')
            else:
                kampanya = Kampanya(urun_id=urun_id, magaza_id=magaza_id, indirim_orani=indirim,
                                    baslangic_tarihi=baslangic, bitis_tarihi=bitis)
                db.session.add(kampanya)
                db.session.commit()
                flash('Kampanya başarıyla oluşturuldu.', 'success')
    kampanyalar = Kampanya.query.filter_by(magaza_id=magaza_id, aktif_mi=True).all()
    # Build urunler list from stoklar for the product select dropdown
    stoklar = Stok.query.filter_by(magaza_id=magaza_id).join(Urun).filter(Urun.aktif_mi == True).all()
    urunler = []
    seen = set()
    for s in stoklar:
        if s.urun_id not in seen:
            seen.add(s.urun_id)
            urun = s.urun
            urun.stok_adedi = s.stok_adedi
            urunler.append(urun)
    return render_template('manager/campaign_form.html',
                           kampanyalar=kampanyalar,
                           urunler=urunler,
                           now=datetime.utcnow())

@manager_bp.route('/campaigns/<int:kampanya_id>/delete', methods=['POST'])
@login_required
@role_required(2)
def delete_campaign(kampanya_id):
    kampanya = Kampanya.query.get_or_404(kampanya_id)
    kampanya.aktif_mi = False  # Soft delete
    db.session.commit()
    flash('Kampanya kaldırıldı.', 'success')
    return redirect(url_for('manager.campaigns'))
