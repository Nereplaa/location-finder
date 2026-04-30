import logging
from datetime import datetime
from flask import current_app
from flask_mail import Message
from ..extensions import db, mail
from ..models.bildirim_talepleri import BildirimTalebi

logger = logging.getLogger(__name__)

def _eposta_gonder(talep):
    """Tek bir bildirim talebi için e-posta gönderir. Hata sessizce loglanır."""
    try:
        msg = Message(
            subject='Ürün Stoka Girdi — AKİS AVM',
            recipients=[talep.eposta],
        )
        msg.body = (
            f'Merhaba,\n\n'
            f'Takip ettiğiniz ürün tekrar stoka girdi.\n'
            f'AVM\'yi ziyaret ederek ürünü inceleyebilirsiniz.\n\n'
            f'AKİS Akıllı AVM Sistemi'
        )
        msg.html = (
            f'<p>Merhaba,</p>'
            f'<p>Takip ettiğiniz ürün <strong>tekrar stoka girdi</strong>.</p>'
            f'<p>AVM\'yi ziyaret ederek ürünü inceleyebilirsiniz.</p>'
            f'<br><p><em>AKİS Akıllı AVM Sistemi</em></p>'
        )
        mail.send(msg)
        logger.info(f'E-posta gönderildi: {talep.eposta}')
    except Exception as e:
        logger.error(f'E-posta gönderilemedi: {talep.eposta} — {e}')

def bildirim_tetikle(urun_id):
    """BR-3.2: Stok min seviyesini aşınca bekleyen talepleri işaretle ve bildir."""
    bekleyenler = BildirimTalebi.query.filter_by(urun_id=urun_id, bildirildi_mi=False).all()
    for talep in bekleyenler:
        talep.bildirildi_mi = True
        talep.bildirim_tarihi = datetime.utcnow()
        _eposta_gonder(talep)
        logger.info(f'Bildirim tetiklendi: urun_id={urun_id}, eposta={talep.eposta}')
    db.session.commit()
    return len(bekleyenler)
