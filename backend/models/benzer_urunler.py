from ..extensions import db

class BenzerUrun(db.Model):
    __tablename__ = 'benzer_urunler'
    id = db.Column(db.Integer, primary_key=True)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    benzer_urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    urun = db.relationship('Urun', foreign_keys=[urun_id], backref='benzer_urun_kayitlari')
    benzer_urun = db.relationship('Urun', foreign_keys=[benzer_urun_id], backref='benzer_olarak_eklenenler')
