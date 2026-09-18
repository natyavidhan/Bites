import logging
import os

from flask import Flask, jsonify, render_template, request

from app.config import Config

# Static assets live in a top-level public/static directory (not
# app/static) because Vercel serves files under public/** straight from
# its CDN and recommends against relying on Flask's own static handling.
# Pointing Flask's static folder at the same directory keeps url_for()
# output identical and lets local dev (flask run / test client) serve
# the very same files.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STATIC_FOLDER = os.path.join(_PROJECT_ROOT, "public", "static")


def create_app() -> Flask:
    app = Flask(__name__, static_folder=_STATIC_FOLDER, static_url_path="/static")
    app.config.from_object(Config)

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("404.html"), 404

    @app.errorhandler(413)
    def too_large(_e):
        message = "Upload is too large."
        if request.path.startswith("/dashboard/api/"):
            return jsonify({"error": message}), 413
        return message, 413

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
