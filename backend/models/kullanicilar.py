from datetime import datetime
from flask_login import UserMixin
from ..extensions import db, login_manager

class Kullanici(UserMixin, db.Model):
    __tablename__ = 'kullanicilar'
    id = db.Column(db.Integer, primary_key=True)
    eposta = db.Column(db.String(120), unique=True, nullable=False)
    sifre_hash = db.Column(db.String(256), nullable=False)
    ad = db.Column(db.String(80), nullable=False)
    soyad = db.Column(db.String(80), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roller.id'), nullable=False)
    aktif_mi = db.Column(db.Boolean, default=True, nullable=False)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    son_giris_tarihi = db.Column(db.DateTime)
    bildirim_talepleri = db.relationship('BildirimTalebi', backref='kullanici', lazy=True)
    magaza_sorumluluklar = db.relationship('MagazaSorumlusu', backref='kullanici', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return Kullanici.query.get(int(user_id))
