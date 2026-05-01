from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from ..models.kullanicilar import Kullanici
from ..utils.validators import gecerli_eposta, gecerli_sifre

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.rol_id == 4:
            return redirect(url_for('kiosk.index'))
        return redirect(url_for('customer.index'))
    if request.method == 'POST':
        eposta = request.form.get('eposta', '').strip()
        sifre = request.form.get('sifre', '')
        kullanici = Kullanici.query.filter_by(eposta=eposta, aktif_mi=True).first()
        if kullanici and check_password_hash(kullanici.sifre_hash, sifre):
            login_user(kullanici)
            session.permanent = True
            if kullanici.rol_id == 4:
                return redirect(url_for('kiosk.index'))
            if kullanici.rol_id == 2:
                return redirect(url_for('manager.dashboard'))
            if kullanici.rol_id == 3:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('customer.index'))
        flash('E-posta veya şifre hatalı. Lütfen tekrar deneyin.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        eposta = request.form.get('eposta', '').strip()
        sifre = request.form.get('sifre', '')
        ad = request.form.get('ad', '').strip()
        soyad = request.form.get('soyad', '').strip()
        if not gecerli_eposta(eposta):
            flash('Geçerli bir e-posta adresi giriniz.', 'danger')
            return render_template('auth/register.html')
        if not gecerli_sifre(sifre):
            flash('Şifre en az 8 karakter olmalıdır.', 'danger')
            return render_template('auth/register.html')
        if Kullanici.query.filter_by(eposta=eposta).first():
            flash('Bu e-posta adresi zaten kayıtlı.', 'danger')
            return render_template('auth/register.html')
        yeni_kullanici = Kullanici(
            eposta=eposta,
            sifre_hash=generate_password_hash(sifre),
            ad=ad, soyad=soyad, rol_id=1
        )
        db.session.add(yeni_kullanici)
        db.session.commit()
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')
