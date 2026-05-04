from datetime import datetime
from flask import Blueprint, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import exists, or_
from ..extensions import db
from ..models.urunler import Urun
from ..models.stoklar import Stok
from ..models.kampanyalar import Kampanya
from ..models.kategoriler import Kategori
from ..models.markalar import Marka
from ..models.magazalar import Magaza
from ..models.urun_ozellikleri import UrunOzelligi
from ..models.benzer_urunler import BenzerUrun
from ..models.arama_gecmisi import AramaGecmisi
from ..models.urun_goruntuleme import UrunGoruntuleme
from ..utils.decorators import role_required

kiosk_bp = Blueprint('kiosk', __name__)

SAYFA_BOYUTU = 8  # 2 sütun × 4 satır


def _kaydet_arama(q):
    if not q:
        return
    try:
        kullanici_id = current_user.id if current_user.is_authenticated else None
        db.session.add(AramaGecmisi(arama_metni=q, kullanici_id=kullanici_id, kaynak='kiosk'))
        db.session.commit()
    except Exception:
        db.session.rollback()


def _kaydet_goruntuleme(urun_id):
    try:
        db.session.add(UrunGoruntuleme(urun_id=urun_id, kaynak='kiosk'))
        db.session.commit()
    except Exception:
        db.session.rollback()


@kiosk_bp.route('/')
@role_required(4)
def index():
    kategoriler = Kategori.query.filter_by(aktif_mi=True, ust_kategori_id=None).all()
    kampanyalar = (Kampanya.query
                   .filter_by(aktif_mi=True)
                   .filter(Kampanya.bitis_tarihi >= datetime.now())
                   .limit(6).all())
    return render_template('kiosk/index.html', kategoriler=kategoriler, kampanyalar=kampanyalar)


@kiosk_bp.route('/products')
@role_required(4)
def products():
    q = request.args.get('q', '').strip()
    kategori_id = request.args.get('kategori_id')
    marka_ids = request.args.getlist('marka_id')
    renkler_filtre = request.args.getlist('renk')
    bedenler_filtre = request.args.getlist('beden')
    stok_filtre = request.args.get('stok')
    sayfa = request.args.get('sayfa', 1, type=int)

    # GÖREV 1: Arama geçmişi kaydı
    _kaydet_arama(q)

    sorgu = Urun.query.filter_by(aktif_mi=True)
    if q:
        sorgu = sorgu.filter(Urun.urun_adi.ilike(f'%{q}%'))
    if kategori_id:
        sorgu = sorgu.filter_by(kategori_id=kategori_id)
    if marka_ids:
        sorgu = sorgu.filter(Urun.marka_id.in_(marka_ids))
    if renkler_filtre or bedenler_filtre:
        sorgu = sorgu.join(UrunOzelligi)
        if renkler_filtre:
            sorgu = sorgu.filter(UrunOzelligi.renk.in_(renkler_filtre))
        if bedenler_filtre:
            sorgu = sorgu.filter(UrunOzelligi.beden.in_(bedenler_filtre))
    if stok_filtre == 'var':
        sorgu = sorgu.filter(
            exists().where((Stok.urun_id == Urun.id) & (Stok.stok_adedi > 0))
        )

    toplam = sorgu.distinct().count()
    toplam_sayfa = max(1, (toplam + SAYFA_BOYUTU - 1) // SAYFA_BOYUTU)
    sayfa = max(1, min(sayfa, toplam_sayfa))
    urunler = sorgu.distinct().offset((sayfa - 1) * SAYFA_BOYUTU).limit(SAYFA_BOYUTU).all()

    markalar = Marka.query.filter_by(aktif_mi=True).all()
    kategoriler = Kategori.query.filter_by(aktif_mi=True).all()
    renkler = [r[0] for r in db.session.query(UrunOzelligi.renk)
               .filter(UrunOzelligi.renk.isnot(None)).distinct().all()]
    bedenler = [b[0] for b in db.session.query(UrunOzelligi.beden)
                .filter(UrunOzelligi.beden.isnot(None)).distinct().all()]

    base_args = {}
    for key in request.args:
        if key == 'sayfa':
            continue
        vals = request.args.getlist(key)
        base_args[key] = vals if len(vals) > 1 else vals[0]

    prev_url = url_for('kiosk.products', sayfa=sayfa - 1, **base_args) if sayfa > 1 else None
    next_url = url_for('kiosk.products', sayfa=sayfa + 1, **base_args) if sayfa < toplam_sayfa else None

    return render_template('kiosk/products.html',
                           urunler=urunler, markalar=markalar, kategoriler=kategoriler,
                           renkler=renkler, bedenler=bedenler,
                           sayfa=sayfa, toplam_sayfa=toplam_sayfa, toplam=toplam,
                           prev_url=prev_url, next_url=next_url)


@kiosk_bp.route('/products/<int:urun_id>')
@role_required(4)
def product_detail(urun_id):
    urun = Urun.query.filter_by(id=urun_id, aktif_mi=True).first_or_404()

    # GÖREV 3: Görüntülenme kaydı
    _kaydet_goruntuleme(urun_id)

    stoklar = Stok.query.filter_by(urun_id=urun_id).all()
    kampanyalar = (Kampanya.query
                   .filter_by(urun_id=urun_id, aktif_mi=True)
                   .filter(Kampanya.bitis_tarihi >= datetime.now())
                   .all())
    aktif_kampanya = kampanyalar[0] if kampanyalar else None

    # GÖREV 7: Benzer ürünler — DB kaydı yoksa kategori/marka bazlı fallback
    benzer_ids = [b.benzer_urun_id for b in BenzerUrun.query.filter_by(urun_id=urun_id).all()]
    if benzer_ids:
        benzer_urunler = (Urun.query.filter(Urun.id.in_(benzer_ids), Urun.aktif_mi == True).all())
    else:
        benzer_urunler = (Urun.query
                          .filter(Urun.id != urun_id, Urun.aktif_mi == True)
                          .filter(
                              or_(Urun.kategori_id == urun.kategori_id,
                                  Urun.marka_id == urun.marka_id)
                          )
                          .limit(4).all())

    tum_magazalar = Magaza.query.filter_by(aktif_mi=True).all()
    return render_template('kiosk/product_detail.html',
                           urun=urun, stoklar=stoklar,
                           kampanyalar=kampanyalar, aktif_kampanya=aktif_kampanya,
                           benzer_urunler=benzer_urunler, tum_magazalar=tum_magazalar)


@kiosk_bp.route('/campaigns')
@role_required(4)
def campaigns():
    kampanyalar = (Kampanya.query
                   .filter_by(aktif_mi=True)
                   .filter(Kampanya.bitis_tarihi >= datetime.now())
                   .all())
    return render_template('kiosk/campaigns.html', kampanyalar=kampanyalar)
