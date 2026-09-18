from flask import Blueprint, redirect, render_template, request, url_for

from app.auth import check_admin_credentials, is_admin_logged_in, login_admin, logout_admin

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if is_admin_logged_in():
            return redirect(url_for("admin.dashboard"))
        return render_template("login.html", error=None)

    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if check_admin_credentials(username, password):
        login_admin()
        next_path = request.args.get("next") or url_for("admin.dashboard")
        if not next_path.startswith("/"):
            next_path = url_for("admin.dashboard")
        return redirect(next_path)

    return render_template("login.html", error="Invalid username or password."), 401


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    logout_admin()
    return redirect(url_for("auth.login"))
