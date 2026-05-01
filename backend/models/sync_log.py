from datetime import datetime
from ..extensions import db


class SyncLog(db.Model):
    __tablename__ = 'sync_log'
    id = db.Column(db.Integer, primary_key=True)
    magaza_id = db.Column(db.Integer, db.ForeignKey('magazalar.id'), nullable=True)
    hata_turu = db.Column(db.String(100), nullable=False)
    detay = db.Column(db.Text)
    tarih = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    cozuldu_mu = db.Column(db.Boolean, default=False, nullable=False)

    magaza = db.relationship('Magaza', backref='sync_loglar', lazy=True)
