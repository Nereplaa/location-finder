from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import exists
from ..extensions import db
from ..models.urunler import Urun
from ..models.stoklar import Stok
from ..models.kampanyalar import Kampanya
from ..models.bildirim_talepleri import BildirimTalebi
from ..models.kategoriler import Kategori
from ..models.markalar import Marka
from ..models.magazalar import Magaza
from ..models.urun_ozellikleri import UrunOzelligi
from ..models.benzer_urunler import BenzerUrun

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
def index():
    kategoriler = Kategori.query.filter_by(aktif_mi=True, ust_kategori_id=None).all()
    kampanyalar = Kampanya.query.filter_by(aktif_mi=True).filter(Kampanya.bitis_tarihi >= datetime.utcnow()).all()
    magazalar = Magaza.query.filter_by(aktif_mi=True).all()
    return render_template('customer/index.html', kategoriler=kategoriler, kampanyalar=kampanyalar, magazalar=magazalar)

@customer_bp.route('/products')
@customer_bp.route('/api/search')
def products():
    q = request.args.get('q', '').strip()
    kategori_id = request.args.get('kategori_id')   # Fixed: was 'kategori'
    marka_ids = request.args.getlist('marka_id')    # Fixed: was single 'marka', now supports multiple checkboxes
    magaza_id = request.args.get('magaza_id')        # New: store filter from index.html store cards
    renkler_filtre = request.args.getlist('renk')
    bedenler_filtre = request.args.getlist('beden')
    fiyat_min = request.args.get('fiyat_min', type=float)
    fiyat_max = request.args.get('fiyat_max', type=float)
    stok_filtre = request.args.get('stok')           # 'var' = only show in-stock products

    sorgu = Urun.query.filter_by(aktif_mi=True)  # BR-2.4

    if q:
        sorgu = sorgu.filter(Urun.urun_adi.ilike(f'%{q}%'))
    if kategori_id:
        sorgu = sorgu.filter_by(kategori_id=kategori_id)
    if marka_ids:
        sorgu = sorgu.filter(Urun.marka_id.in_(marka_ids))
    if fiyat_min is not None:
        sorgu = sorgu.filter(Urun.baz_fiyat >= fiyat_min)
    if fiyat_max is not None:
        sorgu = sorgu.filter(Urun.baz_fiyat <= fiyat_max)

    # Renk ve beden filtresi (FR-1.2) — join only when needed
    if renkler_filtre or bedenler_filtre:
        sorgu = sorgu.join(UrunOzelligi)
        if renkler_filtre:
            sorgu = sorgu.filter(UrunOzelligi.renk.in_(renkler_filtre))
        if bedenler_filtre:
            sorgu = sorgu.filter(UrunOzelligi.beden.in_(bedenler_filtre))

    # Stok filtresi — use EXISTS subquery to avoid join conflicts
    if stok_filtre == 'var':
        sorgu = sorgu.filter(
            exists().where((Stok.urun_id == Urun.id) & (Stok.stok_adedi > 0))
        )

    # Mağaza filtresi — use EXISTS subquery
    if magaza_id:
        try:
            magaza_id_int = int(magaza_id)
            sorgu = sorgu.filter(
                exists().where((Stok.urun_id == Urun.id) & (Stok.magaza_id == magaza_id_int))
            )
        except (ValueError, TypeError):
            pass

    urunler = sorgu.distinct().all()
    markalar = Marka.query.filter_by(aktif_mi=True).all()
    kategoriler = Kategori.query.filter_by(aktif_mi=True).all()
    renkler = [r[0] for r in db.session.query(UrunOzelligi.renk).filter(UrunOzelligi.renk.isnot(None)).distinct().all()]
    bedenler = [b[0] for b in db.session.query(UrunOzelligi.beden).filter(UrunOzelligi.beden.isnot(None)).distinct().all()]
    return render_template('customer/products.html', urunler=urunler, markalar=markalar,
                           kategoriler=kategoriler, renkler=renkler, bedenler=bedenler)

@customer_bp.route('/api/products/<int:urun_id>')
def product_detail(urun_id):
    urun = Urun.query.filter_by(id=urun_id, aktif_mi=True).first_or_404()
    stoklar = Stok.query.filter_by(urun_id=urun_id).all()
    kampanyalar = Kampanya.query.filter_by(urun_id=urun_id, aktif_mi=True).filter(
        Kampanya.bitis_tarihi >= datetime.utcnow()
    ).all()
    aktif_kampanya = kampanyalar[0] if kampanyalar else None
    # Benzer ürünler
    benzer_ids = [b.benzer_urun_id for b in BenzerUrun.query.filter_by(urun_id=urun_id).all()]
    benzer_urunler = Urun.query.filter(Urun.id.in_(benzer_ids), Urun.aktif_mi == True).all() if benzer_ids else []
    return render_template('customer/product_detail.html', urun=urun, stoklar=stoklar, kampanyalar=kampanyalar, aktif_kampanya=aktif_kampanya, benzer_urunler=benzer_urunler)

@customer_bp.route('/api/campaigns')
def campaigns():
    kampanyalar = Kampanya.query.filter_by(aktif_mi=True).filter(
        Kampanya.bitis_tarihi >= datetime.utcnow()
    ).all()
    return render_template('customer/campaigns.html', kampanyalar=kampanyalar)

@customer_bp.route('/api/notifications', methods=['POST'])
@login_required  # BR-1.2
def create_notification():
    urun_id = request.form.get('urun_id', type=int)
    eposta = request.form.get('eposta', '').strip()
    telefon = request.form.get('telefon', '').strip()

    # BR-3.3: 24 saat spam engeli
    son_24_saat = datetime.utcnow() - timedelta(hours=24)
    mevcut = BildirimTalebi.query.filter_by(
        urun_id=urun_id, kullanici_id=current_user.id
    ).filter(BildirimTalebi.talep_tarihi >= son_24_saat).first()

    if mevcut:
        flash('Bu ürün için zaten bir bildirim talebiniz bulunuyor. 24 saat sonra tekrar deneyebilirsiniz.', 'warning')
        return redirect(url_for('customer.product_detail', urun_id=urun_id))

    talep = BildirimTalebi(urun_id=urun_id, kullanici_id=current_user.id, eposta=eposta, telefon=telefon)
    db.session.add(talep)
    db.session.commit()
    flash('Bildirim talebiniz alındı. Ürün stoka girdiğinde haberdar edileceksiniz.', 'success')
    return redirect(url_for('customer.product_detail', urun_id=urun_id))
