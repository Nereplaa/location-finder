from datetime import datetime
from ..extensions import db


class StokLog(db.Model):
    __tablename__ = 'stok_log'
    id = db.Column(db.Integer, primary_key=True)
    stok_id = db.Column(db.Integer, db.ForeignKey('stoklar.id'), nullable=True)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    magaza_id = db.Column(db.Integer, db.ForeignKey('magazalar.id'), nullable=False)
    eski_adet = db.Column(db.Integer, nullable=False)
    yeni_adet = db.Column(db.Integer, nullable=False)
    guncelleme_turu = db.Column(db.String(20), nullable=False)  # 'Manuel' | 'Otomatik'
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)
    tarih = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    urun = db.relationship('Urun', backref='stok_loglar', lazy=True)
    magaza = db.relationship('Magaza', backref='stok_loglar', lazy=True)
