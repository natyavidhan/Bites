import secrets
from functools import wraps

from flask import current_app, jsonify, request


def _provided_api_key() -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return request.headers.get("X-API-Key", "").strip()


def require_api_key(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        expected_key = current_app.config["API_KEY"]
        if not expected_key:
            return jsonify({"error": "The public API is not enabled on this deployment (API_KEY is not set)."}), 503

        provided_key = _provided_api_key()
        if not provided_key or not secrets.compare_digest(provided_key, expected_key):
            return jsonify({"error": "Invalid or missing API key."}), 401

        return view(*args, **kwargs)

    return wrapped
