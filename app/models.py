from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from app.db import get_sites_collection


def _now():
    return datetime.now(timezone.utc)


def to_object_id(id_str: str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None


def serialize_site(doc: dict, include_secrets: bool = False) -> dict:
    """Convert a Mongo site document into a JSON-safe dict for API responses."""
    if not doc:
        return {}
    out = {
        "id": str(doc["_id"]),
        "slug": doc.get("slug"),
        "title": doc.get("title"),
        "source_type": doc.get("source_type"),
        "markdown_theme": doc.get("markdown_theme"),
        "is_public": bool(doc.get("is_public")),
        "protected": bool(doc.get("protected")),
        "protect_username": doc.get("protect_username") if doc.get("protected") else None,
        "created_at": doc["created_at"].isoformat() if doc.get("created_at") else None,
        "updated_at": doc["updated_at"].isoformat() if doc.get("updated_at") else None,
    }
    if include_secrets:
        out["raw_content"] = doc.get("raw_content", "")
    return out


def slug_exists(slug: str, exclude_id=None) -> bool:
    query = {"slug": slug}
    if exclude_id is not None:
        query["_id"] = {"$ne": exclude_id}
    return get_sites_collection().find_one(query, {"_id": 1}) is not None


def list_sites() -> list[dict]:
    cursor = get_sites_collection().find().sort("updated_at", -1)
    return [serialize_site(doc) for doc in cursor]


def get_site_by_slug(slug: str) -> dict | None:
    return get_sites_collection().find_one({"slug": slug})


def get_site_by_id(site_id: str) -> dict | None:
    oid = to_object_id(site_id)
    if oid is None:
        return None
    return get_sites_collection().find_one({"_id": oid})


def get_site_by_slug_or_id(ident: str) -> dict | None:
    """Look up a site by its Mongo id, falling back to its slug.

    Convenient for the public API, where callers more naturally refer to a
    site by the slug they chose rather than its database id.
    """
    oid = to_object_id(ident)
    if oid is not None:
        site = get_sites_collection().find_one({"_id": oid})
        if site:
            return site
    return get_sites_collection().find_one({"slug": ident})


def create_site(fields: dict) -> str:
    now = _now()
    doc = {
        **fields,
        "created_at": now,
        "updated_at": now,
    }
    result = get_sites_collection().insert_one(doc)
    return str(result.inserted_id)


def update_site(site_id: str, updates: dict) -> bool:
    oid = to_object_id(site_id)
    if oid is None:
        return False
    updates = {**updates, "updated_at": _now()}
    result = get_sites_collection().update_one({"_id": oid}, {"$set": updates})
    return result.matched_count > 0


def delete_site(site_id: str) -> bool:
    oid = to_object_id(site_id)
    if oid is None:
        return False
    result = get_sites_collection().delete_one({"_id": oid})
    return result.deleted_count > 0
