from flask import Flask
from flask import render_template

from app.admin import admin_bp
from app.auth import auth_bp
from app.cli import register_cli_commands
from app.config import config_by_name
from app.extensions import bcrypt, csrf, db, login_manager, migrate
from app.main import main_bp
from app.models import Usuario
from app.security import configure_security_headers


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    selected_config = config_name or "default"
    app.config.from_object(config_by_name[selected_config])

    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_cli_commands(app)
    configure_security_headers(app)

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(Usuario, int(user_id))
