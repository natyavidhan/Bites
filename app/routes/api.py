"""Public REST API (/api/v1/*), authenticated with a bearer API key.

This is the surface the Bites MCP server (or any other external tool)
talks to. It mirrors the dashboard's site-management API but takes JSON
instead of multipart form data, since callers here are agents/scripts
generating content rather than a browser uploading a file.
"""
import secrets

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from app.api_auth import require_api_key
from app.markdown_themes import DEFAULT_THEME, THEME_CATALOG, is_valid_theme
from app.models import (
    create_site,
    delete_site,
    get_site_by_id,
    get_site_by_slug_or_id,
    list_sites,
    serialize_site,
    slug_exists,
    update_site,
)
from app.utils.render import render_markdown_document
from app.utils.slugs import is_valid_slug, slug_error, slugify
from app.utils.validation import validate_protection_fields

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

MAX_TITLE_LENGTH = 200


def _json_body() -> dict:
    return request.get_json(silent=True) or {}


def _site_url(slug: str) -> str:
    return request.host_url.rstrip("/") + "/" + slug


def _generate_unique_slug(basis: str) -> str | None:
    base = slugify(basis)[:60]
    if not is_valid_slug(base):
        base = "site"
    if not slug_exists(base):
        return base
    for _ in range(20):
        candidate = f"{base}-{secrets.token_hex(3)}"
        if not slug_exists(candidate):
            return candidate
    return None


@api_bp.route("/ping", methods=["GET"])
@require_api_key
def ping():
    return jsonify({"ok": True, "service": "bites"})


@api_bp.route("/themes", methods=["GET"])
@require_api_key
def list_themes():
    return jsonify({"themes": THEME_CATALOG})


@api_bp.route("/sites", methods=["GET"])
@require_api_key
def api_list_sites():
    return jsonify({"sites": list_sites()})


@api_bp.route("/sites/<ident>", methods=["GET"])
@require_api_key
def api_get_site(ident):
    site = get_site_by_slug_or_id(ident)
    if not site:
        return jsonify({"error": "Site not found."}), 404
    out = serialize_site(site, include_secrets=True)
    out["url"] = _site_url(site["slug"])
    return jsonify({"site": out})


@api_bp.route("/sites", methods=["POST"])
@require_api_key
def api_create_site():
    data = _json_body()

    title = (data.get("title") or "").strip()[:MAX_TITLE_LENGTH]
    content = data.get("content")
    source_type = data.get("source_type")
    is_public = bool(data.get("is_public", True))
    protected = bool(data.get("protected", False))
    protect_username = (data.get("protect_username") or "").strip()
    protect_password = data.get("protect_password") or ""

    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "content is required."}), 400
    if source_type not in ("html", "markdown"):
        return jsonify({"error": "source_type must be 'html' or 'markdown'."}), 400

    slug = (data.get("slug") or "").strip().lower()
    if slug:
        err = slug_error(slug)
        if err:
            return jsonify({"error": err}), 400
        if slug_exists(slug):
            return jsonify({"error": f'The name "{slug}" is already taken.'}), 409
    else:
        slug = _generate_unique_slug(title or content)
        if not slug:
            return jsonify({"error": "Could not generate a unique slug; provide one explicitly."}), 400

    err = validate_protection_fields(protected, protect_username, protect_password, is_update=False, keep_existing=False)
    if err:
        return jsonify({"error": err}), 400

    markdown_theme = None
    if source_type == "markdown":
        markdown_theme = (data.get("markdown_theme") or DEFAULT_THEME).strip()
        if not is_valid_theme(markdown_theme):
            return jsonify({"error": "Unknown Markdown theme."}), 400

    rendered_html = (
        render_markdown_document(content, title or slug, markdown_theme)
        if source_type == "markdown"
        else content
    )

    fields = {
        "slug": slug,
        "title": title or slug,
        "source_type": source_type,
        "raw_content": content,
        "rendered_html": rendered_html,
        "markdown_theme": markdown_theme,
        "is_public": is_public,
        "protected": protected,
        "protect_username": protect_username if protected else None,
        "protect_password_hash": generate_password_hash(protect_password) if protected else None,
    }
    site_id = create_site(fields)
    site = get_site_by_id(site_id)
    out = serialize_site(site)
    out["url"] = _site_url(site["slug"])
    return jsonify({"site": out}), 201


@api_bp.route("/sites/<ident>", methods=["PATCH", "PUT"])
@require_api_key
def api_update_site(ident):
    site = get_site_by_slug_or_id(ident)
    if not site:
        return jsonify({"error": "Site not found."}), 404
    site_id = str(site["_id"])

    data = _json_body()
    updates = {}

    if "slug" in data:
        slug = (data.get("slug") or "").strip().lower()
        err = slug_error(slug)
        if err:
            return jsonify({"error": err}), 400
        if slug_exists(slug, exclude_id=site["_id"]):
            return jsonify({"error": f'The name "{slug}" is already taken.'}), 409
        updates["slug"] = slug

    if "title" in data:
        updates["title"] = (data.get("title") or "").strip()[:MAX_TITLE_LENGTH] or site["title"]

    if "is_public" in data:
        updates["is_public"] = bool(data["is_public"])

    protected = bool(data.get("protected", site.get("protected", False))) if "protected" in data else site.get("protected", False)
    protect_username = (data.get("protect_username") or "").strip()
    protect_password = data.get("protect_password") or ""
    keep_existing_password = protected and site.get("protected") and not protect_password

    if "protected" in data or "protect_username" in data or "protect_password" in data:
        err = validate_protection_fields(
            protected, protect_username or site.get("protect_username", ""), protect_password,
            is_update=True, keep_existing=keep_existing_password,
        )
        if err:
            return jsonify({"error": err}), 400

        updates["protected"] = protected
        if not protected:
            updates["protect_username"] = None
            updates["protect_password_hash"] = None
        else:
            updates["protect_username"] = protect_username or site.get("protect_username")
            if protect_password:
                updates["protect_password_hash"] = generate_password_hash(protect_password)

    content = data.get("content")
    source_type = data.get("source_type")
    if content is not None and not isinstance(content, str):
        return jsonify({"error": "content must be a string."}), 400
    if source_type is not None and source_type not in ("html", "markdown"):
        return jsonify({"error": "source_type must be 'html' or 'markdown'."}), 400

    effective_source_type = source_type or site.get("source_type")
    effective_title = updates.get("title", site.get("title"))

    theme_changed = False
    effective_theme = site.get("markdown_theme") or DEFAULT_THEME
    if effective_source_type == "markdown":
        if "markdown_theme" in data:
            requested_theme = (data.get("markdown_theme") or "").strip()
            if not is_valid_theme(requested_theme):
                return jsonify({"error": "Unknown Markdown theme."}), 400
            theme_changed = requested_theme != effective_theme
            effective_theme = requested_theme
        updates["markdown_theme"] = effective_theme
    elif source_type is not None:
        updates["markdown_theme"] = None

    if content is not None:
        updates["raw_content"] = content
        updates["source_type"] = source_type or site.get("source_type")
        updates["rendered_html"] = (
            render_markdown_document(content, effective_title, effective_theme)
            if updates["source_type"] == "markdown"
            else content
        )
    elif effective_source_type == "markdown" and (("title" in updates) or theme_changed):
        updates["rendered_html"] = render_markdown_document(
            site.get("raw_content", ""), effective_title, effective_theme
        )

    update_site(site_id, updates)
    updated = get_site_by_id(site_id)
    out = serialize_site(updated)
    out["url"] = _site_url(updated["slug"])
    return jsonify({"site": out})


@api_bp.route("/sites/<ident>", methods=["DELETE"])
@require_api_key
def api_delete_site(ident):
    site = get_site_by_slug_or_id(ident)
    if not site:
        return jsonify({"error": "Site not found."}), 404
    delete_site(str(site["_id"]))
    return jsonify({"ok": True})
