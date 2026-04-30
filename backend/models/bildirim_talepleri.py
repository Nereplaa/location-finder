from datetime import datetime
from ..extensions import db

class BildirimTalebi(db.Model):
    __tablename__ = 'bildirim_talepleri'
    id = db.Column(db.Integer, primary_key=True)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)
    eposta = db.Column(db.String(120), nullable=False)
    telefon = db.Column(db.String(20))
    talep_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    bildirildi_mi = db.Column(db.Boolean, default=False, nullable=False)
    bildirim_tarihi = db.Column(db.DateTime, nullable=True)
