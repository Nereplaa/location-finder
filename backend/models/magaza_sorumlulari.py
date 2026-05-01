from datetime import datetime
from ..extensions import db


class MagazaSorumlusu(db.Model):
    __tablename__ = 'magaza_sorumlulari'
    id = db.Column(db.Integer, primary_key=True)
    magaza_id = db.Column(db.Integer, db.ForeignKey('magazalar.id'), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    atama_tarihi = db.Column(db.DateTime, default=datetime.utcnow)

