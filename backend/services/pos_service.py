import logging
from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models.stoklar import Stok
from ..services.stock_service import stok_guncelle

logger = logging.getLogger(__name__)
pos_bp = Blueprint('pos', __name__)

def _dogrula_api_key():
    """POS API key doğrulaması. Header veya query param üzerinden kabul eder."""
    beklenen = current_app.config.get('POS_API_KEY', '')
    gelen = request.headers.get('X-API-Key') or request.args.get('api_key', '')
    return gelen == beklenen

@pos_bp.route('/api/pos/stock-update', methods=['POST'])
def pos_stock_update():
    """FR-4.3: POS'tan gelen otomatik stok sync. BR-2.2: tutarsızlık loglanır.

    JSON body: { urun_id, magaza_id, satis_adedi }
    satis_adedi: satılan adet (stoktan düşülür). BR-2.2: mevcut stok < satis_adedi
    ise işlem yine yapılır, stok 0'a çekilir ve tutarsızlık loglanır.
    """
    if not _dogrula_api_key():
        logger.warning(f'POS yetkisiz erişim girişimi: {request.remote_addr}')
        return jsonify({'hata': 'Geçersiz veya eksik API anahtarı'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'hata': 'JSON gövdesi gerekli'}), 400

    urun_id = data.get('urun_id')
    magaza_id = data.get('magaza_id')
    satis_adedi = data.get('satis_adedi')

    if urun_id is None or magaza_id is None or satis_adedi is None:
        return jsonify({'hata': 'Eksik parametre: urun_id, magaza_id, satis_adedi gerekli'}), 400

    if not isinstance(satis_adedi, int) or satis_adedi <= 0:
        return jsonify({'hata': 'satis_adedi pozitif tam sayı olmalıdır'}), 400

    try:
        stok = Stok.query.filter_by(urun_id=urun_id, magaza_id=magaza_id).first()
        if not stok:
            return jsonify({'hata': 'Ürün veya mağaza bulunamadı'}), 404

        if satis_adedi > stok.stok_adedi:
            # BR-2.2: POS verisi > mevcut stok — işlemi yap, tutarsızlığı logla
            logger.warning(
                f'POS tutarsızlık: urun_id={urun_id}, magaza_id={magaza_id}, '
                f'satis_adedi={satis_adedi}, mevcut_stok={stok.stok_adedi}'
            )
            yeni_adet = 0
        else:
            yeni_adet = stok.stok_adedi - satis_adedi

        stok = stok_guncelle(urun_id, magaza_id, yeni_adet, 'Otomatik')
        return jsonify({'durum': 'basarili', 'stok_adedi': stok.stok_adedi}), 200
    except Exception as e:
        logger.error(f'POS sync basarisiz: {e}')  # FR-4.4
        return jsonify({'hata': 'Sistem hatası oluştu'}), 500
