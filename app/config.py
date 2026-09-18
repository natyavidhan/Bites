import os

# Slugs that a hosted site is not allowed to claim, because they are
# used for the app's own routes.
RESERVED_SLUGS = {
    "dashboard",
    "login",
    "logout",
    "static",
    "api",
    "favicon.ico",
    "robots.txt",
    "",
}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB = os.environ.get("MONGODB_DB", "bites")

    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_BYTES", 2 * 1024 * 1024))  # 2 MB

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("VERCEL", "") != "" or os.environ.get(
        "FORCE_SECURE_COOKIES", ""
    ) == "1"
