from datetime import datetime
from ..extensions import db

class Stok(db.Model):
    __tablename__ = 'stoklar'
    id = db.Column(db.Integer, primary_key=True)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    magaza_id = db.Column(db.Integer, db.ForeignKey('magazalar.id'), nullable=False)
    stok_adedi = db.Column(db.Integer, default=0, nullable=False)  # BR-2.1: >= 0
    min_stok_seviyesi = db.Column(db.Integer, default=5, nullable=False)
    guncelleme_turu = db.Column(db.Enum('Manuel', 'Otomatik', name='guncelleme_turu_enum'), nullable=False)  # BR-4.2
    son_guncelleme_tarihi = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    son_guncelleyen_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)
    son_guncelleyen = db.relationship('Kullanici', backref='guncellenen_stoklar', lazy=True)

    __table_args__ = (
        db.CheckConstraint('stok_adedi >= 0', name='stok_negatif_olamaz'),  # BR-2.1
    )
