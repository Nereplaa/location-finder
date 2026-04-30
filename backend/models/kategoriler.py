from ..extensions import db

class Kategori(db.Model):
    __tablename__ = 'kategoriler'
    id = db.Column(db.Integer, primary_key=True)
    kategori_adi = db.Column(db.String(100), nullable=False)
    ust_kategori_id = db.Column(db.Integer, db.ForeignKey('kategoriler.id'), nullable=True)
    aktif_mi = db.Column(db.Boolean, default=True, nullable=False)
    alt_kategoriler = db.relationship('Kategori', backref=db.backref('ust_kategori', remote_side=[id]))
    urunler = db.relationship('Urun', backref='kategori', lazy=True)
