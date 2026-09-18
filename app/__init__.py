import logging

from flask import Flask

from app.config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.db import ensure_indexes

    try:
        with app.app_context():
            ensure_indexes()
    except Exception:  # pragma: no cover - best effort, DB may be briefly unreachable
        logging.getLogger(__name__).warning("Could not ensure MongoDB indexes on startup", exc_info=True)

    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.site import site_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(site_bp)

    return app
