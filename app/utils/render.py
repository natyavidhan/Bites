import html as html_lib

import markdown as md

EXTENSION_TYPES = {
    "html": "html",
    "htm": "html",
    "md": "markdown",
    "markdown": "markdown",
}

MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "toc", "sane_lists", "nl2br"]

_MARKDOWN_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{
    max-width: 820px;
    margin: 40px auto;
    padding: 0 20px 80px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #1f2328;
    background: #fff;
  }}
  h1, h2, h3, h4 {{ line-height: 1.25; margin-top: 1.6em; }}
  h1 {{ border-bottom: 1px solid #d1d9e0; padding-bottom: .3em; }}
  h2 {{ border-bottom: 1px solid #d1d9e0; padding-bottom: .3em; }}
  a {{ color: #0969da; }}
  pre {{
    background: #f6f8fa;
    padding: 16px;
    overflow: auto;
    border-radius: 6px;
  }}
  code {{
    background: #f6f8fa;
    padding: .2em .4em;
    border-radius: 6px;
    font-size: 85%;
  }}
  pre code {{ background: none; padding: 0; }}
  blockquote {{
    border-left: 4px solid #d1d9e0;
    margin: 0;
    padding: 0 1em;
    color: #59636e;
  }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #d1d9e0; padding: 6px 13px; }}
  img {{ max-width: 100%; }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #0d1117; color: #e6edf3; }}
    h1, h2 {{ border-color: #30363d; }}
    pre, code {{ background: #161b22; }}
    blockquote {{ border-color: #30363d; color: #8d96a0; }}
    th, td {{ border-color: #30363d; }}
    a {{ color: #4493f8; }}
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def detect_source_type(filename: str) -> str | None:
    if not filename or "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[1].lower()
    return EXTENSION_TYPES.get(ext)


def render_markdown_document(markdown_text: str, title: str) -> str:
    """Render Markdown source into a complete, styled HTML document."""
    body = md.markdown(markdown_text, extensions=MARKDOWN_EXTENSIONS)
    return _MARKDOWN_PAGE_TEMPLATE.format(title=html_lib.escape(title or "Untitled"), body=body)
