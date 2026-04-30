from datetime import datetime
from ..extensions import db

class Kampanya(db.Model):
    __tablename__ = 'kampanyalar'
    id = db.Column(db.Integer, primary_key=True)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    magaza_id = db.Column(db.Integer, db.ForeignKey('magazalar.id'), nullable=False)
    indirim_orani = db.Column(db.Numeric(5, 2), nullable=False)
    baslangic_tarihi = db.Column(db.DateTime, nullable=False)
    bitis_tarihi = db.Column(db.DateTime, nullable=False)  # BR-3.1: bitis > baslangic
    aktif_mi = db.Column(db.Boolean, default=True, nullable=False)
    magaza = db.relationship('Magaza', backref='kampanyalar', lazy=True)

    __table_args__ = (
        db.CheckConstraint('bitis_tarihi > baslangic_tarihi', name='kampanya_tarih_kontrolu'),  # BR-3.1
    )
