import re

from app.config import RESERVED_SLUGS

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Turn arbitrary text into a URL-safe slug."""
    text = (text or "").strip().lower()
    text = _NON_ALNUM_RE.sub("-", text)
    return text.strip("-")


def is_valid_slug(slug: str) -> bool:
    if not slug or len(slug) > 80:
        return False
    if slug in RESERVED_SLUGS:
        return False
    return bool(_SLUG_RE.match(slug))


def slug_error(slug: str) -> str | None:
    """Return a human-readable validation error, or None if the slug is fine."""
    if not slug:
        return "Site name cannot be empty."
    if len(slug) > 80:
        return "Site name is too long (max 80 characters)."
    if slug in RESERVED_SLUGS:
        return f'"{slug}" is a reserved name and cannot be used.'
    if not _SLUG_RE.match(slug):
        return "Site name can only contain lowercase letters, numbers, and hyphens."
    return None
