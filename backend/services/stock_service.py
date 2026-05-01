import logging
from datetime import datetime
from ..extensions import db
from ..models.stoklar import Stok
from ..models.stok_log import StokLog
from ..services.notification_service import bildirim_tetikle

logger = logging.getLogger(__name__)


def stok_guncelle(urun_id, magaza_id, yeni_adet, guncelleme_turu, guncelleyen_id=None):
    """BR-2.1: stok negatife düşemez. BR-4.2: güncelleme türü + StokLog kaydedilir."""
    if yeni_adet < 0:  # BR-2.1
        raise ValueError('Stok adedi negatif olamaz.')

    stok = Stok.query.filter_by(urun_id=urun_id, magaza_id=magaza_id).first()
    if not stok:
        stok = Stok(urun_id=urun_id, magaza_id=magaza_id, stok_adedi=0, guncelleme_turu=guncelleme_turu)
        db.session.add(stok)
        db.session.flush()

    eski_adet = stok.stok_adedi  # denetim izi için kaydet

    stok.stok_adedi = yeni_adet
    stok.guncelleme_turu = guncelleme_turu  # BR-4.2
    stok.son_guncelleme_tarihi = datetime.utcnow()
    stok.son_guncelleyen_id = guncelleyen_id

    # StokLog kaydı — her değişimi izle (BR-4.2 + denetim izi)
    log = StokLog(
        stok_id=stok.id,
        urun_id=urun_id,
        magaza_id=magaza_id,
        eski_adet=eski_adet,
        yeni_adet=yeni_adet,
        guncelleme_turu=guncelleme_turu,
        kullanici_id=guncelleyen_id,
    )
    db.session.add(log)
    db.session.commit()

    # BR-3.2: stok min seviyesini aştıysa bildirimleri tetikle
    if stok.stok_adedi > stok.min_stok_seviyesi:
        bildirim_tetikle(urun_id)

    return stok
