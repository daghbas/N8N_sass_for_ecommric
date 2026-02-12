from flask import Flask

from app.api.routes import support_bp
from app.core.config import Settings
from app.core.db import db
from app.core.logging import configure_logging
from app.services.n8n_client import N8NClient
from app.services.support_service import SupportService
from app.web.routes import web_bp


def create_app() -> Flask:
    settings = Settings.from_env()
    configure_logging(settings.log_level)

    app = Flask(__name__)
    app.config["SETTINGS"] = settings
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    n8n_client = N8NClient(settings)
    support_service = SupportService(settings, n8n_client)
    app.config["SUPPORT_SERVICE"] = support_service

    app.register_blueprint(web_bp)
    app.register_blueprint(support_bp, url_prefix="/api/v1")

    @app.get("/health")
    def health() -> tuple[dict, int]:
        return {"status": "ok"}, 200

    with app.app_context():
        from app import models  # noqa: F401

        db.create_all()

    return app
