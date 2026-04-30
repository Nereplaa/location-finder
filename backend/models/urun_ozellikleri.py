from ..extensions import db

class UrunOzelligi(db.Model):
    __tablename__ = 'urun_ozellikleri'
    id = db.Column(db.Integer, primary_key=True)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    renk = db.Column(db.String(50))
    beden = db.Column(db.String(20))
    kumas_turu = db.Column(db.String(100))
    ek_fiyat = db.Column(db.Numeric(10, 2), default=0)
