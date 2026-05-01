from datetime import datetime
from ..extensions import db


class AramaGecmisi(db.Model):
    __tablename__ = 'arama_gecmisi'
    id = db.Column(db.Integer, primary_key=True)
    arama_metni = db.Column(db.String(500), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)
    tarih = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    kaynak = db.Column(db.String(20), default='web', nullable=False)  # 'web' | 'kiosk'

    kullanici = db.relationship('Kullanici', backref='aramalar', lazy=True)
