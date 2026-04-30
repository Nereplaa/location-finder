from ..extensions import db

class Marka(db.Model):
    __tablename__ = 'markalar'
    id = db.Column(db.Integer, primary_key=True)
    marka_adi = db.Column(db.String(100), unique=True, nullable=False)
    aktif_mi = db.Column(db.Boolean, default=True, nullable=False)
    urunler = db.relationship('Urun', backref='marka', lazy=True)
