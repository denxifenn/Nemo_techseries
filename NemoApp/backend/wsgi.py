from .app import create_app

# WSGI entrypoint for production servers (e.g., gunicorn).
# Usage (from repo root):
#   gunicorn NemoApp.backend.wsgi:app --workers 2 --threads 8 --timeout 120 --bind 0.0.0.0:$PORT
#
# Render.com / Railway deploy guides are provided in DEPLOYMENT_GUIDE.md

app = create_app()