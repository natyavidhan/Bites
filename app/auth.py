import secrets
from functools import wraps

from flask import current_app, jsonify, redirect, request, session, url_for


def check_admin_credentials(username: str, password: str) -> bool:
    expected_user = current_app.config["ADMIN_USERNAME"]
    expected_pass = current_app.config["ADMIN_PASSWORD"]
    if not expected_user or not expected_pass:
        # Admin login has not been configured via environment variables.
        return False
    user_ok = secrets.compare_digest(username or "", expected_user)
    pass_ok = secrets.compare_digest(password or "", expected_pass)
    return user_ok and pass_ok


def is_admin_logged_in() -> bool:
    return bool(session.get("is_admin"))


def login_admin() -> None:
    session.clear()
    session["is_admin"] = True
    session.permanent = True


def logout_admin() -> None:
    session.clear()


def require_admin(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not is_admin_logged_in():
            if request.path.startswith("/dashboard/api/"):
                return jsonify({"error": "Authentication required."}), 401
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped
