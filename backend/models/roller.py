from ..extensions import db

class Rol(db.Model):
    __tablename__ = 'roller'
    id = db.Column(db.Integer, primary_key=True)
    rol_adi = db.Column(db.String(50), unique=True, nullable=False)
    aciklama = db.Column(db.String(200))
    kullanicilar = db.relationship('Kullanici', backref='rol', lazy=True)
