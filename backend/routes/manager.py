from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from ..extensions import db
from ..models.urunler import Urun
from ..models.stoklar import Stok
from ..models.kampanyalar import Kampanya
from ..models.magaza_sorumlulari import MagazaSorumlusu
from ..models.magazalar import Magaza
from ..models.kategoriler import Kategori
from ..models.markalar import Marka
from ..models.urun_ozellikleri import UrunOzelligi
from ..models.stok_log import StokLog
from ..models.urun_goruntuleme import UrunGoruntuleme
from ..utils.decorators import role_required
from ..services.stock_service import stok_guncelle

manager_bp = Blueprint('manager', __name__)


def get_sorumlu_magaza_id():
    """Giriş yapan sorumluya ait mağaza id'sini döner (BR-1.1)"""
    atama = MagazaSorumlusu.query.filter_by(kullanici_id=current_user.id).first()
    return atama.magaza_id if atama else None


def _ozellik_kaydet(urun_id, form):
    """GÖREV 6: Form'dan renk/beden/kumaş satırlarını UrunOzelligi olarak kaydeder."""
    idx = 0
    while True:
        renk = (form.get(f'renk_{idx}') or '').strip()
        beden = (form.get(f'beden_{idx}') or '').strip()
        kumas = (form.get(f'kumas_{idx}') or '').strip()
        ek_fiyat_str = form.get(f'ekfiyat_{idx}', '0')
        if not renk and not beden and not kumas:
            break
        try:
            ek_fiyat = float(ek_fiyat_str) if ek_fiyat_str else 0.0
        except ValueError:
            ek_fiyat = 0.0
        db.session.add(UrunOzelligi(
            urun_id=urun_id,
            renk=renk or None,
            beden=beden or None,
            kumas_turu=kumas or None,
            ek_fiyat=ek_fiyat
        ))
        idx += 1
        if idx > 50:
            break


@manager_bp.route('/dashboard')
@login_required
@role_required(2)
def dashboard():
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

    # GÖREV 2: Son stok hareketleri (StokLog tablosundan)
    urun_idleri = [s.urun_id for s in tum_stoklar]
    stok_loglar = (StokLog.query
                   .filter(StokLog.magaza_id == magaza_id)
                   .order_by(StokLog.tarih.desc())
                   .limit(10).all())

    # GÖREV 3: Görüntülenme istatistikleri
    son_30 = datetime.utcnow() - timedelta(days=30)
    # Top 5 ürün — bu mağazadaki ürünler için görüntülenme sayısı
    goruntuleme_ozet = (db.session.query(UrunGoruntuleme.urun_id, func.count(UrunGoruntuleme.id).label('sayi'))
                        .filter(UrunGoruntuleme.urun_id.in_(urun_idleri))
                        .filter(UrunGoruntuleme.tarih >= son_30)
                        .group_by(UrunGoruntuleme.urun_id)
                        .order_by(func.count(UrunGoruntuleme.id).desc())
                        .limit(5).all())
    populer_urunler = []
    for row in goruntuleme_ozet:
        urun = Urun.query.get(row.urun_id)
        if urun:
            populer_urunler.append({'urun': urun, 'sayi': row.sayi})

    # Bugün görüntülenme
    bugun_baslangic = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    bugun_goruntuleme = (UrunGoruntuleme.query
                         .filter(UrunGoruntuleme.urun_id.in_(urun_idleri))
                         .filter(UrunGoruntuleme.tarih >= bugun_baslangic)
                         .count())

    # Son 7 gün günlük görüntülenme (Chart.js line chart için)
    today = datetime.utcnow().date()
    goruntuleme_istatistikleri = []
    for i in range(6, -1, -1):
        gun = today - timedelta(days=i)
        gun_dt = datetime(gun.year, gun.month, gun.day)
        sayi = (UrunGoruntuleme.query
                .filter(UrunGoruntuleme.urun_id.in_(urun_idleri))
                .filter(UrunGoruntuleme.tarih >= gun_dt,
                        UrunGoruntuleme.tarih < gun_dt + timedelta(days=1))
                .count())
        goruntuleme_istatistikleri.append({'gun': gun.strftime('%d.%m'), 'sayi': sayi})

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
                           stok_loglar=stok_loglar,
                           populer_urunler=populer_urunler,
                           bugun_goruntuleme=bugun_goruntuleme,
                           goruntuleme_istatistikleri=goruntuleme_istatistikleri)


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
        min_stok_seviyesi = request.form.get('min_stok_seviyesi', 5, type=int)
        if stok_adedi < 0:
            stok_adedi = 0
        if min_stok_seviyesi < 0:
            min_stok_seviyesi = 0
        urun = Urun(urun_adi=urun_adi, marka_id=marka_id, kategori_id=kategori_id,
                    baz_fiyat=baz_fiyat, aciklama=aciklama, gorsel_url=gorsel_url)
        db.session.add(urun)
        db.session.flush()
        stok = Stok(urun_id=urun.id, magaza_id=magaza_id, stok_adedi=stok_adedi,
                    min_stok_seviyesi=min_stok_seviyesi, guncelleme_turu='Manuel')
        db.session.add(stok)
        # GÖREV 6: UrunOzellikleri kaydet
        _ozellik_kaydet(urun.id, request.form)
        db.session.commit()
        flash('Ürün başarıyla eklendi.', 'success')

    q = request.args.get('q', '').strip()
    stok_filtre = request.args.get('stok_filtre', '')
    sorgu = Stok.query.filter_by(magaza_id=magaza_id).join(Urun).filter(Urun.aktif_mi == True)
    if q:
        sorgu = sorgu.filter(Urun.urun_adi.ilike(f'%{q}%'))
    if stok_filtre == 'tukendi':
        sorgu = sorgu.filter(Stok.stok_adedi == 0)
    elif stok_filtre == 'kritik':
        sorgu = sorgu.filter(Stok.stok_adedi > 0, Stok.stok_adedi <= Stok.min_stok_seviyesi)
    elif stok_filtre == 'normal':
        sorgu = sorgu.filter(Stok.stok_adedi > Stok.min_stok_seviyesi)
    stoklar = sorgu.all()
    urunler = []
    for s in stoklar:
        urun = s.urun
        urun.stok = s
        urunler.append(urun)
    markalar = Marka.query.filter_by(aktif_mi=True).all()
    kategoriler = Kategori.query.filter_by(aktif_mi=True).all()
    return render_template('manager/products.html', urunler=urunler, stoklar=stoklar,
                           markalar=markalar, kategoriler=kategoriler)


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
    stok = Stok.query.filter_by(urun_id=urun_id, magaza_id=magaza_id).first()
    if not stok:
        flash('Bu ürün üzerinde yetkiniz yok.', 'danger')
        return redirect(url_for('manager.products')), 403
    urun = Urun.query.get_or_404(urun_id)
    urun.aktif_mi = False
    db.session.commit()
    flash('Ürün pasif hale getirildi.', 'success')
    return redirect(url_for('manager.products'))


@manager_bp.route('/products/<int:urun_id>/update', methods=['POST'])
@login_required
@role_required(2)
def update_product(urun_id):
    """FR-2.1: Ürün bilgileri + UrunOzellikleri güncelleme (BR-1.1)"""
    magaza_id = get_sorumlu_magaza_id()
    stok = Stok.query.filter_by(urun_id=urun_id, magaza_id=magaza_id).first()
    if not stok:
        flash('Bu ürün üzerinde yetkiniz yok.', 'danger')
        return redirect(url_for('manager.products'))
    urun = Urun.query.get_or_404(urun_id)
    urun_adi = request.form.get('urun_adi', '').strip()
    if urun_adi:
        urun.urun_adi = urun_adi
    marka_id = request.form.get('marka_id', type=int)
    if marka_id:
        urun.marka_id = marka_id
    kategori_id = request.form.get('kategori_id', type=int)
    if kategori_id:
        urun.kategori_id = kategori_id
    baz_fiyat = request.form.get('baz_fiyat', type=float)
    if baz_fiyat is not None and baz_fiyat >= 0:
        urun.baz_fiyat = baz_fiyat
    aciklama = request.form.get('aciklama', '').strip()
    if aciklama:
        urun.aciklama = aciklama
    gorsel_url = request.form.get('gorsel_url', '').strip()
    if gorsel_url:
        urun.gorsel_url = gorsel_url
    min_stok = request.form.get('min_stok_seviyesi', type=int)
    if min_stok is not None and min_stok >= 0:
        stok.min_stok_seviyesi = min_stok
    # GÖREV 6: Yeni özellik satırları varsa ekle (mevcut özellikleri silmeden)
    if request.form.get('renk_0') or request.form.get('beden_0') or request.form.get('kumas_0'):
        _ozellik_kaydet(urun_id, request.form)
    db.session.commit()
    flash('Ürün başarıyla güncellendi.', 'success')
    return redirect(url_for('manager.products'))


@manager_bp.route('/products/<int:urun_id>/reset-stock', methods=['POST'])
@login_required
@role_required(2)
def reset_stock(urun_id):
    magaza_id = get_sorumlu_magaza_id()
    stok = Stok.query.filter_by(urun_id=urun_id, magaza_id=magaza_id).first()
    if not stok:
        flash('Bu ürün üzerinde yetkiniz yok.', 'danger')
        return redirect(url_for('manager.products')), 403
    stok_guncelle(urun_id, magaza_id, 0, 'Manuel', current_user.id)
    flash('Stok sıfırlandı.', 'success')
    return redirect(url_for('manager.products'))


@manager_bp.route('/campaigns', methods=['GET', 'POST'])
@login_required
@role_required(2)
def campaigns():
    magaza_id = get_sorumlu_magaza_id()
    if request.method == 'POST':
        urun_id = request.form.get('urun_id', type=int)
        indirim = request.form.get('indirim_orani', type=float)
        baslangic_str = request.form.get('baslangic_tarihi', '')
        bitis_str = request.form.get('bitis_tarihi', '')
        try:
            fmt = '%Y-%m-%dT%H:%M' if 'T' in baslangic_str else '%Y-%m-%d'
            baslangic = datetime.strptime(baslangic_str, fmt)
            bitis = datetime.strptime(bitis_str, '%Y-%m-%dT%H:%M' if 'T' in bitis_str else '%Y-%m-%d')
        except (ValueError, TypeError):
            flash('Geçersiz tarih formatı.', 'danger')
            baslangic = bitis = None
        if baslangic and bitis:
            if bitis <= baslangic:
                flash('Bitiş tarihi başlangıç tarihinden sonra olmalıdır.', 'danger')
            else:
                kampanya = Kampanya(urun_id=urun_id, magaza_id=magaza_id, indirim_orani=indirim,
                                    baslangic_tarihi=baslangic, bitis_tarihi=bitis)
                db.session.add(kampanya)
                db.session.commit()
                flash('Kampanya başarıyla oluşturuldu.', 'success')
    kampanyalar = Kampanya.query.filter_by(magaza_id=magaza_id, aktif_mi=True).all()
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
    kampanya.aktif_mi = False
    db.session.commit()
    flash('Kampanya kaldırıldı.', 'success')
    return redirect(url_for('manager.campaigns'))
