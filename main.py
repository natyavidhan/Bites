"""Zero-config entrypoint for Vercel's Python runtime.

Vercel auto-detects a Flask instance named `app` in main.py (or app.py,
index.py, server.py, wsgi.py, asgi.py) at the project root and deploys
it as a single Vercel Function; every request that doesn't match a file
under public/** is routed here.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
