import markdown as md

from app.markdown_themes import DEFAULT_THEME, render_themed_document

EXTENSION_TYPES = {
    "html": "html",
    "htm": "html",
    "md": "markdown",
    "markdown": "markdown",
}

MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "toc", "sane_lists", "nl2br"]


def detect_source_type(filename: str) -> str | None:
    if not filename or "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[1].lower()
    return EXTENSION_TYPES.get(ext)


def render_markdown_document(markdown_text: str, title: str, theme: str = DEFAULT_THEME) -> str:
    """Render Markdown source into a complete, themed HTML document."""
    body_html = md.markdown(markdown_text, extensions=MARKDOWN_EXTENSIONS)
    return render_themed_document(title, body_html, theme)
