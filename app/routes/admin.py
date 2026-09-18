import markdown as md
from flask import Blueprint, Response, jsonify, render_template, request
from werkzeug.security import generate_password_hash

from app.auth import require_admin
from app.markdown_themes import DEFAULT_THEME, THEME_CATALOG, is_valid_theme, render_themed_document
from app.models import (
    create_site,
    delete_site,
    get_site_by_id,
    list_sites,
    serialize_site,
    slug_exists,
    update_site,
)
from app.utils.render import MARKDOWN_EXTENSIONS, detect_source_type, render_markdown_document
from app.utils.slugs import slug_error
from app.utils.validation import validate_protection_fields

_SAMPLE_MARKDOWN = """# Sample document

This is a **preview** of how a Markdown page looks with this theme.

## Features

- Inline `code`, [links](#), and *emphasis*
- Fenced code blocks
- Tables and blockquotes

```python
def hello():
    print("Hello from Bites!")
```

> A blockquote, for good measure.

| Column A | Column B |
| -------- | -------- |
| foo      | bar      |
"""

admin_bp = Blueprint("admin", __name__, url_prefix="/dashboard")

MAX_TITLE_LENGTH = 200


def _bool_field(name: str, default: bool = False) -> bool:
    value = request.form.get(name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "on", "yes")


def _read_uploaded_content():
    """Return (raw_content, source_type, error_message) from the request.

    A single file upload takes priority; otherwise falls back to pasted
    text content with an explicit source_type field.
    """
    upload = request.files.get("file")
    if upload and upload.filename:
        source_type = detect_source_type(upload.filename)
        if source_type is None:
            return None, None, "Unsupported file type. Upload a .html, .htm, .md, or .markdown file."
        raw_bytes = upload.read()
        try:
            raw_content = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return None, None, "File must be UTF-8 encoded text."
        return raw_content, source_type, None

    content = request.form.get("content")
    source_type = request.form.get("source_type")
    if content is not None and content.strip() != "":
        if source_type not in ("html", "markdown"):
            return None, None, "source_type must be 'html' or 'markdown'."
        return content, source_type, None

    return None, None, None


@admin_bp.route("/")
@require_admin
def dashboard():
    return render_template("dashboard.html")


@admin_bp.route("/api/sites", methods=["GET"])
@require_admin
def api_list_sites():
    return jsonify({"sites": list_sites()})


@admin_bp.route("/api/sites/<site_id>", methods=["GET"])
@require_admin
def api_get_site(site_id):
    site = get_site_by_id(site_id)
    if not site:
        return jsonify({"error": "Site not found."}), 404
    return jsonify({"site": serialize_site(site, include_secrets=True)})


@admin_bp.route("/api/sites", methods=["POST"])
@require_admin
def api_create_site():
    slug = (request.form.get("slug") or "").strip().lower()
    title = (request.form.get("title") or slug).strip()[:MAX_TITLE_LENGTH]
    is_public = _bool_field("is_public", default=True)
    protected = _bool_field("protected", default=False)
    protect_username = (request.form.get("protect_username") or "").strip()
    protect_password = request.form.get("protect_password") or ""

    err = slug_error(slug)
    if err:
        return jsonify({"error": err}), 400
    if slug_exists(slug):
        return jsonify({"error": f'The name "{slug}" is already taken.'}), 409

    err = validate_protection_fields(protected, protect_username, protect_password, is_update=False, keep_existing=False)
    if err:
        return jsonify({"error": err}), 400

    raw_content, source_type, err = _read_uploaded_content()
    if err:
        return jsonify({"error": err}), 400
    if raw_content is None:
        return jsonify({"error": "Upload a file or paste content for the site."}), 400

    markdown_theme = None
    if source_type == "markdown":
        markdown_theme = (request.form.get("markdown_theme") or DEFAULT_THEME).strip()
        if not is_valid_theme(markdown_theme):
            return jsonify({"error": "Unknown Markdown theme."}), 400

    rendered_html = (
        render_markdown_document(raw_content, title, markdown_theme)
        if source_type == "markdown"
        else raw_content
    )

    fields = {
        "slug": slug,
        "title": title,
        "source_type": source_type,
        "raw_content": raw_content,
        "rendered_html": rendered_html,
        "markdown_theme": markdown_theme,
        "is_public": is_public,
        "protected": protected,
        "protect_username": protect_username if protected else None,
        "protect_password_hash": generate_password_hash(protect_password) if protected else None,
    }
    site_id = create_site(fields)
    return jsonify({"site": serialize_site(get_site_by_id(site_id))}), 201


@admin_bp.route("/api/sites/<site_id>", methods=["PATCH", "PUT"])
@require_admin
def api_update_site(site_id):
    site = get_site_by_id(site_id)
    if not site:
        return jsonify({"error": "Site not found."}), 404

    updates = {}

    if "slug" in request.form:
        slug = (request.form.get("slug") or "").strip().lower()
        err = slug_error(slug)
        if err:
            return jsonify({"error": err}), 400
        if slug_exists(slug, exclude_id=site["_id"]):
            return jsonify({"error": f'The name "{slug}" is already taken.'}), 409
        updates["slug"] = slug

    if "title" in request.form:
        updates["title"] = (request.form.get("title") or "").strip()[:MAX_TITLE_LENGTH] or site["title"]

    if "is_public" in request.form:
        updates["is_public"] = _bool_field("is_public", default=site.get("is_public", True))

    protected = _bool_field("protected", default=site.get("protected", False)) if "protected" in request.form else site.get("protected", False)
    protect_username = (request.form.get("protect_username") or "").strip()
    protect_password = request.form.get("protect_password") or ""
    keep_existing_password = protected and site.get("protected") and not protect_password

    if "protected" in request.form or "protect_username" in request.form or "protect_password" in request.form:
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

    raw_content, source_type, err = _read_uploaded_content()
    if err:
        return jsonify({"error": err}), 400

    effective_source_type = source_type or site.get("source_type")
    effective_title = updates.get("title", site.get("title"))

    theme_changed = False
    effective_theme = site.get("markdown_theme") or DEFAULT_THEME
    if effective_source_type == "markdown":
        if "markdown_theme" in request.form:
            requested_theme = (request.form.get("markdown_theme") or "").strip()
            if not is_valid_theme(requested_theme):
                return jsonify({"error": "Unknown Markdown theme."}), 400
            theme_changed = requested_theme != effective_theme
            effective_theme = requested_theme
        updates["markdown_theme"] = effective_theme
    elif source_type is not None:
        # content type explicitly switched away from markdown this update
        updates["markdown_theme"] = None

    if raw_content is not None:
        updates["raw_content"] = raw_content
        updates["source_type"] = source_type
        updates["rendered_html"] = (
            render_markdown_document(raw_content, effective_title, effective_theme)
            if source_type == "markdown"
            else raw_content
        )
    elif effective_source_type == "markdown" and (("title" in updates) or theme_changed):
        # Re-render so the <title> and/or theme in the generated document stay in sync.
        updates["rendered_html"] = render_markdown_document(
            site.get("raw_content", ""), effective_title, effective_theme
        )

    update_site(site_id, updates)
    return jsonify({"site": serialize_site(get_site_by_id(site_id))})


@admin_bp.route("/api/themes", methods=["GET"])
@require_admin
def api_list_themes():
    return jsonify({"themes": THEME_CATALOG})


@admin_bp.route("/api/theme-preview", methods=["GET"])
@require_admin
def api_theme_preview():
    theme = request.args.get("theme", DEFAULT_THEME)
    if not is_valid_theme(theme):
        return jsonify({"error": "Unknown theme."}), 400
    body_html = md.markdown(_SAMPLE_MARKDOWN, extensions=MARKDOWN_EXTENSIONS)
    html_doc = render_themed_document("Theme preview", body_html, theme)
    return Response(html_doc, mimetype="text/html")


@admin_bp.route("/api/sites/<site_id>/toggle-visibility", methods=["POST"])
@require_admin
def api_toggle_visibility(site_id):
    site = get_site_by_id(site_id)
    if not site:
        return jsonify({"error": "Site not found."}), 404
    new_value = not bool(site.get("is_public"))
    update_site(site_id, {"is_public": new_value})
    return jsonify({"site": serialize_site(get_site_by_id(site_id))})


@admin_bp.route("/api/sites/<site_id>", methods=["DELETE"])
@require_admin
def api_delete_site(site_id):
    if not get_site_by_id(site_id):
        return jsonify({"error": "Site not found."}), 404
    delete_site(site_id)
    return jsonify({"ok": True})
