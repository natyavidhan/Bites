"""MongoDB connection helpers.

Serverless platforms like Vercel reuse the Python process between
invocations while it stays warm, so we cache the client at module level
instead of reconnecting on every request.
"""
from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        from flask import current_app

        uri = current_app.config["MONGODB_URI"]
        _client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    return _client


def get_db():
    from flask import current_app

    return get_client()[current_app.config["MONGODB_DB"]]


def get_sites_collection() -> Collection:
    return get_db()["sites"]


def ensure_indexes() -> None:
    get_sites_collection().create_index([("slug", ASCENDING)], unique=True)
