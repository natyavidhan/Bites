"""Theme catalog for rendered Markdown pages.

Two families:
  - "classic": the 12 official GitHub Pages themes (github.com/pages-themes,
    CC0-licensed). Each has its own authentic wrapper markup, ported from
    the real theme's _layouts/default.html with GitHub-repo-specific bits
    (fork/download buttons, "maintained by" attribution) removed, paired
    with its real stylesheet compiled from the theme's SCSS source.
  - "modern": a handful of popular color schemes (GitHub, Dracula, Nord,
    Solarized, Gruvbox) applied to one shared, simple article layout.

Every renderer only needs `title` and `body_html` (the markdown already
converted to HTML) and returns a complete, self-contained HTML document
with the theme's CSS inlined.
"""
import html
import os

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "theme_assets")
_css_cache: dict[str, str] = {}

DEFAULT_THEME = "github-light"


def _read_css(*parts: str) -> str:
    path = os.path.join(_ASSETS_DIR, *parts)
    if path not in _css_cache:
        with open(path, encoding="utf-8") as f:
            _css_cache[path] = f.read()
    return _css_cache[path]


def _doc(title: str, css: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title or "Untitled")}</title>
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>
"""


# --- classic (GitHub Pages) theme wrappers -----------------------------

def _cayman(t, body):
    return f"""
<header class="page-header">
  <h1 class="project-name">{t}</h1>
</header>
<main class="main-content">
{body}
  <footer class="site-footer">
    <span class="site-footer-credits">Published with Bites.</span>
  </footer>
</main>"""


def _architect(t, body):
    return f"""
<header>
  <div class="inner">
    <h1>{t}</h1>
  </div>
</header>
<div id="content-wrapper">
  <div class="inner clearfix">
    <section id="main-content">
{body}
    </section>
    <aside id="sidebar">
      <p>Published with Bites.</p>
    </aside>
  </div>
</div>"""


def _dinky(t, body):
    return f"""
<div class="wrapper">
  <header>
    <h1 class="header">{t}</h1>
  </header>
  <section>
{body}
  </section>
  <footer>
    <p><small>Published with Bites</small></p>
  </footer>
</div>"""


def _hacker(t, body):
    return f"""
<header>
  <div class="container">
    <h1>{t}</h1>
  </div>
</header>
<div class="container">
  <section id="main_content">
{body}
  </section>
</div>"""


def _leap_day(t, body):
    return f"""
<header>
  <h1>{t}</h1>
</header>
<div class="wrapper">
  <nav><ul></ul></nav>
  <section>
{body}
  </section>
  <footer>
    <p><small>Hosted with Bites</small></p>
  </footer>
</div>"""


def _merlot(t, body):
    return f"""
<div class="shell">
  <header>
    <span class="ribbon-outer">
      <span class="ribbon-inner">
        <h1>{t}</h1>
      </span>
      <span class="left-tail"></span>
      <span class="right-tail"></span>
    </span>
  </header>
  <div id="no-downloads">
    <span class="inner"></span>
  </div>
  <span class="banner-fix"></span>
  <section id="main_content">
{body}
  </section>
  <footer>
    <span class="ribbon-outer">
      <span class="ribbon-inner">
        <p>Published with Bites</p>
      </span>
      <span class="left-tail"></span>
      <span class="right-tail"></span>
    </span>
  </footer>
</div>"""


def _midnight(t, body):
    return f"""
<div class="wrapper">
  <section>
    <div id="title">
      <h1>{t}</h1>
      <hr>
    </div>
{body}
  </section>
</div>"""


def _minimal(t, body):
    return f"""
<div class="wrapper">
  <header>
    <h1>{t}</h1>
  </header>
  <section>
{body}
  </section>
  <footer>
    <p><small>Published with Bites</small></p>
  </footer>
</div>"""


def _modernist(t, body):
    return f"""
<div class="wrapper">
  <header class="without-description">
    <h1>{t}</h1>
  </header>
  <section>
{body}
  </section>
</div>
<footer>
  <p>Published with Bites</p>
</footer>"""


def _slate(t, body):
    return f"""
<div id="header_wrap" class="outer">
  <header class="inner">
    <h1 id="project_title">{t}</h1>
  </header>
</div>
<div id="main_content_wrap" class="outer">
  <section id="main_content" class="inner">
{body}
  </section>
</div>
<div id="footer_wrap" class="outer">
  <footer class="inner">
    <p>Published with Bites</p>
  </footer>
</div>"""


def _tactile(t, body):
    return f"""
<div id="container">
  <div class="inner">
    <header>
      <h1>{t}</h1>
    </header>
    <hr>
    <section id="main_content">
{body}
    </section>
    <footer>
      Published with Bites.
    </footer>
  </div>
</div>"""


def _time_machine(t, body):
    return f"""
<div class="wrapper">
  <header>
    <h1 class="title">{t}</h1>
  </header>
  <div id="container">
    <div id="main" role="main">
      <article class="markdown-body">
{body}
      </article>
    </div>
  </div>
  <footer>
    <div class="creds">
      <small>Published with Bites</small>
    </div>
  </footer>
</div>"""


_CLASSIC_WRAPPERS = {
    "cayman": _cayman,
    "architect": _architect,
    "dinky": _dinky,
    "hacker": _hacker,
    "leap-day": _leap_day,
    "merlot": _merlot,
    "midnight": _midnight,
    "minimal": _minimal,
    "modernist": _modernist,
    "slate": _slate,
    "tactile": _tactile,
    "time-machine": _time_machine,
}

_CLASSIC_NAMES = {
    "cayman": "Cayman",
    "architect": "Architect",
    "dinky": "Dinky",
    "hacker": "Hacker",
    "leap-day": "Leap Day",
    "merlot": "Merlot",
    "midnight": "Midnight",
    "minimal": "Minimal",
    "modernist": "Modernist",
    "slate": "Slate",
    "tactile": "Tactile",
    "time-machine": "Time Machine",
}

_MODERN_NAMES = {
    "github-light": "GitHub Light",
    "github-dark": "GitHub Dark",
    "dracula": "Dracula",
    "nord": "Nord",
    "solarized-light": "Solarized Light",
    "solarized-dark": "Solarized Dark",
    "gruvbox-dark": "Gruvbox Dark",
}

THEME_CATALOG = (
    [{"slug": s, "name": n, "family": "modern"} for s, n in _MODERN_NAMES.items()]
    + [{"slug": s, "name": n, "family": "classic"} for s, n in _CLASSIC_NAMES.items()]
)

_VALID_THEMES = {t["slug"] for t in THEME_CATALOG}


def is_valid_theme(slug: str) -> bool:
    return slug in _VALID_THEMES


def render_themed_document(title: str, body_html: str, theme: str = DEFAULT_THEME) -> str:
    if theme in _CLASSIC_WRAPPERS:
        css = _read_css("classic", f"{theme}.css")
        body = _CLASSIC_WRAPPERS[theme](html.escape(title or "Untitled"), body_html)
        return _doc(title, css, body)

    if theme not in _MODERN_NAMES:
        theme = DEFAULT_THEME
    css = _read_css("modern", "_base.css") + "\n" + _read_css("modern", f"{theme}.css")
    body = f"""
<article class="markdown-body">
  <h1 class="doc-title">{html.escape(title or "Untitled")}</h1>
{body_html}
</article>"""
    return _doc(title, css, body)
