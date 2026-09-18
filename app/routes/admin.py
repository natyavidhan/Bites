from flask import Blueprint, render_template

from app.auth import require_admin

admin_bp = Blueprint("admin", __name__, url_prefix="/dashboard")


@admin_bp.route("/")
@require_admin
def dashboard():
    return render_template("dashboard.html")
