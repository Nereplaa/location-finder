from datetime import datetime
from ..extensions import db


class UrunGoruntuleme(db.Model):
    __tablename__ = 'urun_goruntuleme'
    id = db.Column(db.Integer, primary_key=True)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    tarih = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    kaynak = db.Column(db.String(20), default='web', nullable=False)  # 'web' | 'kiosk'

    urun = db.relationship('Urun', backref='goruntulmeler', lazy=True)
