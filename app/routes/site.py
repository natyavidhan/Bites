import secrets

from flask import Blueprint, Response, render_template, request
from werkzeug.security import check_password_hash

from app.auth import is_admin_logged_in
from app.config import RESERVED_SLUGS
from app.models import get_site_by_slug

site_bp = Blueprint("site", __name__)


def _unauthorized(realm: str) -> Response:
    resp = Response("Authentication required.", 401)
    resp.headers["WWW-Authenticate"] = f'Basic realm="{realm}"'
    return resp


def _site_auth_ok(site: dict) -> bool:
    auth = request.authorization
    if auth is None:
        return False
    user_ok = secrets.compare_digest(auth.username or "", site.get("protect_username") or "")
    pass_ok = check_password_hash(site.get("protect_password_hash") or "", auth.password or "")
    return user_ok and pass_ok


@site_bp.route("/")
def landing():
    return render_template("landing.html")


@site_bp.route("/<slug>")
def serve_site(slug):
    if slug in RESERVED_SLUGS:
        return render_template("404.html"), 404

    site = get_site_by_slug(slug)
    if not site:
        return render_template("404.html"), 404

    admin_preview = is_admin_logged_in()

    if not site.get("is_public") and not admin_preview:
        return render_template("404.html"), 404

    if site.get("protected") and not admin_preview:
        if not _site_auth_ok(site):
            return _unauthorized(slug)

    return Response(site.get("rendered_html", ""), mimetype="text/html")
