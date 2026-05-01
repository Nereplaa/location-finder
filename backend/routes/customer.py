from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import exists, or_
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
from ..models.arama_gecmisi import AramaGecmisi
from ..models.urun_goruntuleme import UrunGoruntuleme

customer_bp = Blueprint('customer', __name__)


def _kaydet_arama(q, kaynak='web'):
    """GÖREV 1: Arama metnini AramaGecmisi tablosuna yaz."""
    if not q:
        return
    try:
        kullanici_id = current_user.id if current_user.is_authenticated else None
        db.session.add(AramaGecmisi(arama_metni=q, kullanici_id=kullanici_id, kaynak=kaynak))
        db.session.commit()
    except Exception:
        db.session.rollback()


def _kaydet_goruntuleme(urun_id, kaynak='web'):
    """GÖREV 3: Ürün görüntülenmesini UrunGoruntuleme tablosuna yaz."""
    try:
        db.session.add(UrunGoruntuleme(urun_id=urun_id, kaynak=kaynak))
        db.session.commit()
    except Exception:
        db.session.rollback()


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
    kategori_id = request.args.get('kategori_id')
    marka_ids = request.args.getlist('marka_id')
    magaza_id = request.args.get('magaza_id')
    renkler_filtre = request.args.getlist('renk')
    bedenler_filtre = request.args.getlist('beden')
    kumaslar_filtre = request.args.getlist('kumas_turu')
    fiyat_min = request.args.get('fiyat_min', type=float)
    fiyat_max = request.args.get('fiyat_max', type=float)
    stok_filtre = request.args.get('stok')

    # GÖREV 1: Arama geçmişi kaydı
    _kaydet_arama(q, kaynak='web')

    sorgu = Urun.query.filter_by(aktif_mi=True)  # BR-2.4

    if q:
        marka_q = db.session.query(Marka.id).filter(Marka.marka_adi.ilike(f'%{q}%'))
        sorgu = sorgu.filter(
            or_(Urun.urun_adi.ilike(f'%{q}%'), Urun.marka_id.in_(marka_q))
        )
    if kategori_id:
        try:
            kat_id_int = int(kategori_id)
            # TASK 3: Ana kategori seçilirse alt kategorileri de dahil et
            alt_idler = [k.id for k in Kategori.query.filter_by(
                ust_kategori_id=kat_id_int, aktif_mi=True).all()]
            tum_kat_idler = [kat_id_int] + alt_idler
            sorgu = sorgu.filter(Urun.kategori_id.in_(tum_kat_idler))
        except (ValueError, TypeError):
            pass
    if marka_ids:
        sorgu = sorgu.filter(Urun.marka_id.in_(marka_ids))
    if fiyat_min is not None:
        sorgu = sorgu.filter(Urun.baz_fiyat >= fiyat_min)
    if fiyat_max is not None:
        sorgu = sorgu.filter(Urun.baz_fiyat <= fiyat_max)

    if renkler_filtre or bedenler_filtre or kumaslar_filtre:
        sorgu = sorgu.join(UrunOzelligi)
        if renkler_filtre:
            sorgu = sorgu.filter(UrunOzelligi.renk.in_(renkler_filtre))
        if bedenler_filtre:
            sorgu = sorgu.filter(UrunOzelligi.beden.in_(bedenler_filtre))
        if kumaslar_filtre:
            sorgu = sorgu.filter(UrunOzelligi.kumas_turu.in_(kumaslar_filtre))

    if stok_filtre == 'var':
        sorgu = sorgu.filter(
            exists().where((Stok.urun_id == Urun.id) & (Stok.stok_adedi > 0))
        )

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

    # TASK 3: Hiyerarşik kategori listesi — üst kategoriler + alt kategoriler
    ust_kategoriler = Kategori.query.filter_by(aktif_mi=True, ust_kategori_id=None).all()
    kategori_agaci = []
    for ust in ust_kategoriler:
        alt_katlar = Kategori.query.filter_by(aktif_mi=True, ust_kategori_id=ust.id).all()
        kategori_agaci.append({'ust': ust, 'altlar': alt_katlar})

    kategoriler = Kategori.query.filter_by(aktif_mi=True).all()
    renkler = [r[0] for r in db.session.query(UrunOzelligi.renk).filter(UrunOzelligi.renk.isnot(None)).distinct().all()]
    bedenler = [b[0] for b in db.session.query(UrunOzelligi.beden).filter(UrunOzelligi.beden.isnot(None)).distinct().all()]
    kumaslar = [k[0] for k in db.session.query(UrunOzelligi.kumas_turu).filter(UrunOzelligi.kumas_turu.isnot(None)).distinct().all()]
    return render_template('customer/products.html', urunler=urunler, markalar=markalar,
                           kategoriler=kategoriler, kategori_agaci=kategori_agaci,
                           renkler=renkler, bedenler=bedenler, kumaslar=kumaslar)


@customer_bp.route('/api/products/<int:urun_id>')
def product_detail(urun_id):
    urun = Urun.query.filter_by(id=urun_id, aktif_mi=True).first_or_404()

    # GÖREV 3: Görüntülenme kaydı
    _kaydet_goruntuleme(urun_id, kaynak='web')

    stoklar = Stok.query.filter_by(urun_id=urun_id).all()
    kampanyalar = Kampanya.query.filter_by(urun_id=urun_id, aktif_mi=True).filter(
        Kampanya.bitis_tarihi >= datetime.utcnow()
    ).all()
    aktif_kampanya = kampanyalar[0] if kampanyalar else None

    # GÖREV 7: Benzer ürünler — DB kaydı yoksa kategori/marka bazlı fallback
    benzer_ids = [b.benzer_urun_id for b in BenzerUrun.query.filter_by(urun_id=urun_id).all()]
    if benzer_ids:
        benzer_urunler = Urun.query.filter(Urun.id.in_(benzer_ids), Urun.aktif_mi == True).all()
    else:
        benzer_urunler = (Urun.query
                          .filter(Urun.id != urun_id, Urun.aktif_mi == True)
                          .filter(
                              or_(Urun.kategori_id == urun.kategori_id,
                                  Urun.marka_id == urun.marka_id)
                          )
                          .limit(4).all())

    tum_magazalar = Magaza.query.filter_by(aktif_mi=True).all()
    return render_template('customer/product_detail.html', urun=urun, stoklar=stoklar,
                           kampanyalar=kampanyalar, aktif_kampanya=aktif_kampanya,
                           benzer_urunler=benzer_urunler, tum_magazalar=tum_magazalar)


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
