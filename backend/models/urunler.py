from datetime import datetime
from ..extensions import db

class Urun(db.Model):
    __tablename__ = 'urunler'
    id = db.Column(db.Integer, primary_key=True)
    urun_adi = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    gorsel_url = db.Column(db.String(500))
    marka_id = db.Column(db.Integer, db.ForeignKey('markalar.id'), nullable=False)  # BR-2.3
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategoriler.id'), nullable=False)  # BR-2.3
    baz_fiyat = db.Column(db.Numeric(10, 2), nullable=False)
    aktif_mi = db.Column(db.Boolean, default=True, nullable=False)  # BR-2.4
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    ozellikler = db.relationship('UrunOzelligi', backref='urun', lazy=True)
    stoklar = db.relationship('Stok', backref='urun', lazy=True)
    kampanyalar = db.relationship('Kampanya', backref='urun', lazy=True)
    bildirim_talepleri = db.relationship('BildirimTalebi', backref='urun', lazy=True)
