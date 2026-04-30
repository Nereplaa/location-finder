from flask import Flask
from .extensions import db, login_manager, migrate, csrf, mail
from .config import config

def create_app(config_name='default'):
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)

    from .routes.auth import auth_bp
    from .routes.customer import customer_bp
    from .routes.manager import manager_bp
    from .routes.admin import admin_bp
    from .services.pos_service import pos_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customer_bp, url_prefix='')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(pos_bp)

    # POS endpoint'i CSRF'den muaf tut (API key ile korunuyor)
    csrf.exempt(pos_bp)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()

    @app.errorhandler(401)
    def unauthorized(e):
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        app.logger.error(f'Sunucu hatası: {e}')
        return render_template('errors/500.html'), 500

    return app
