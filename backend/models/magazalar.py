from ..extensions import db

class Magaza(db.Model):
    __tablename__ = 'magazalar'
    id = db.Column(db.Integer, primary_key=True)
    magaza_adi = db.Column(db.String(150), nullable=False)
    kat = db.Column(db.String(10), nullable=False)
    konum_kodu = db.Column(db.String(20), unique=True, nullable=False)  # BR-4.1
    calisma_saati_baslangic = db.Column(db.String(5))
    calisma_saati_bitis = db.Column(db.String(5))
    aciklama = db.Column(db.Text)
    aktif_mi = db.Column(db.Boolean, default=True, nullable=False)
    konum_x = db.Column(db.Integer, nullable=True)   # Harita X koordinatı (piksel)
    konum_y = db.Column(db.Integer, nullable=True)   # Harita Y koordinatı (piksel)
    stoklar = db.relationship('Stok', backref='magaza', lazy=True)
    sorumlular = db.relationship('MagazaSorumlusu', backref='magaza', lazy=True)
