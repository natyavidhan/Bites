# Bites

A tiny, self-hosted GitHub Gist–style publisher. Upload a single HTML file (CSS/JS
inline is fine) or a Markdown file, get a URL. Flask + MongoDB backend, plain
HTML/CSS/JS frontend, deploys to Vercel with zero build configuration.

## Features

- **Admin dashboard** (`/dashboard`) gated by a username/password set via environment
  variables — no signup flow, no user table.
- **Single-file sites**: upload `.html`/`.htm` (served as-is) or `.md`/`.markdown`
  (rendered to styled HTML server-side), or just paste content directly.
- **19 Markdown themes**, picked per site from the dashboard: all 12 official
  GitHub Pages themes (Cayman, Slate, Midnight, Merlot, etc.) plus 7 popular
  modern color schemes (GitHub Light/Dark, Dracula, Nord, Solarized, Gruvbox).
  A "Preview" button opens a sample page in a new tab before you commit to one.
- **Per-site visibility toggle**: flip a site public/private at any time.
- **Per-site password protection**: optionally require its own username/password
  (HTTP Basic Auth), independent of the admin login.
- **Clean URLs**: whatever slug you give a site becomes `yourdomain.com/<slug>`.

## Stack

- Backend: Flask (Python)
- Database: MongoDB (via `pymongo`) — use MongoDB Atlas's free tier for a
  zero-cost deployment
- Frontend: plain HTML/CSS/JS, no build step, no frameworks

## Project layout

```
main.py                 # Vercel/local entrypoint, exports `app`
app/
  __init__.py            # Flask app factory
  config.py               # env-var config + reserved slugs
  db.py                    # cached MongoDB client/collection
  models.py                # site document CRUD + serialization
  auth.py                  # admin session auth
  routes/
    auth.py                 # /login, /logout
    admin.py                 # /dashboard page + JSON API
    site.py                   # "/" landing + "/<slug>" public serving
  templates/                # Jinja templates (login, dashboard, landing, 404)
  utils/
    slugs.py                 # slugify + validation
    render.py                 # Markdown -> HTML conversion
  markdown_themes.py       # theme catalog + per-theme page rendering
  theme_assets/
    classic/                 # the 12 GitHub Pages themes' CSS
    modern/                  # GitHub/Dracula/Nord/Solarized/Gruvbox CSS
public/
  static/                  # CSS/JS served directly by Vercel's CDN
```

## Local development

Requires Python 3.10+ and a MongoDB instance (local `mongod`, Docker, or an
Atlas cluster).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY, MONGODB_URI

python main.py
# -> http://localhost:5000/dashboard
```

## Deploying to Vercel

1. **Create a MongoDB database.** The easiest option is a free
   [MongoDB Atlas](https://www.mongodb.com/atlas) cluster — create one, add a
   database user, allow access from anywhere (`0.0.0.0/0`, since Vercel's
   outbound IPs aren't static), and copy the connection string.
2. **Push this repo to GitHub** (or your git host of choice).
3. **Import the project into Vercel** ([vercel.com/new](https://vercel.com/new)).
   Vercel auto-detects `main.py` as a Python/Flask app — no build command or
   `vercel.json` needed.
4. **Set environment variables** in the Vercel project settings:

   | Variable | Description |
   |---|---|
   | `ADMIN_USERNAME` | Username for the `/dashboard` login |
   | `ADMIN_PASSWORD` | Password for the `/dashboard` login |
   | `SECRET_KEY` | Random string for signing session cookies |
   | `MONGODB_URI` | Your MongoDB / Atlas connection string |
   | `MONGODB_DB` | Database name (default: `bites`) |

5. **Deploy.** Visit `/dashboard`, log in, and create your first site.

## How it works

- `/dashboard` — log in with `ADMIN_USERNAME`/`ADMIN_PASSWORD`, then create,
  edit, delete, and toggle visibility for sites from one page.
- `/<slug>` — any other path is checked against hosted sites. A match serves
  the site's HTML (rendering Markdown on save, not on every request); no
  match (or a private site, viewed while logged out) returns a 404.
- Protected sites prompt the browser's native HTTP Basic Auth dialog using
  the username/password set for that specific site.
- A logged-in admin can always open a private or protected site directly, to
  preview it before publishing.

## Markdown theme credits

The 12 classic themes under `app/theme_assets/classic/` are ported from
[github.com/pages-themes](https://github.com/pages-themes) (CC0-licensed,
public domain) — the same themes GitHub Pages' theme chooser has always
offered. Their SCSS was compiled to plain CSS, GitHub-repo-specific bits
(fork/download buttons, "maintained by" attribution) were stripped, and a
few missing local fonts/background images were swapped for Google Fonts or
embedded as data URIs so every page stays a single self-contained file.

## Security notes

This is designed for a **single trusted admin** — anyone who can log into
`/dashboard` can publish arbitrary HTML and JavaScript, served as-is at your
domain (that's the point: it's a personal gist host, not a multi-tenant
platform for untrusted users). Keep `ADMIN_PASSWORD` and `SECRET_KEY` private,
and put the app behind Vercel's HTTPS (on by default) so credentials and
session cookies aren't sent in the clear.
