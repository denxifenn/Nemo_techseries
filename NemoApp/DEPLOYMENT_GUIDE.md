# Nemo Backend – Deployment Guide (Render.com / Railway)

This guide shows how to deploy the Flask + Firebase Admin backend. It uses gunicorn and a simple WSGI entrypoint.

Key files
- WSGI entry: [backend/wsgi.py](NemoApp/backend/wsgi.py)
- Requirements: [backend/requirements.txt](NemoApp/backend/requirements.txt)
- Firebase Admin service config: [python.initialize_firebase()](NemoApp/backend/services/firebase_service.py:11)
  - Supports env var FIREBASE_CREDENTIALS_PATH to point to the service-account JSON
- App factory: [python.create_app()](NemoApp/backend/app.py:6)

Environment variables (required)
- FIREBASE_CREDENTIALS_PATH
  - Absolute path to your Firebase service-account key JSON on the server.
  - On managed platforms (Render/Railway) you cannot commit the key; upload it as a Secret File and set this env var to the path where the platform stores it at runtime.
- PORT
  - Provided by the platform. gunicorn will bind to 0.0.0.0:$PORT

Optional
- FLASK_ENV=production

Command to run in production
- gunicorn NemoApp.backend.wsgi:app --workers 2 --threads 8 --timeout 120 --bind 0.0.0.0:$PORT

Recommended instance size
- 512 MB RAM with 1 vCPU is typically enough for MVP. Increase if needed.

A) Render.com (Web Service)
1) Create new Web Service
- Build command: (none, Python is interpreted)
- Start command:
  - gunicorn NemoApp.backend.wsgi:app --workers 2 --threads 8 --timeout 120 --bind 0.0.0.0:$PORT

2) Environment
- Add environment variable:
  - FIREBASE_CREDENTIALS_PATH=/opt/render/project/src/service-account.json (example)
- Secret file (Service Account JSON)
  - Upload your Firebase service-account JSON as a Secret File and place it at /opt/render/project/src/service-account.json
  - Set FIREBASE_CREDENTIALS_PATH accordingly.

3) Deploy
- Render will install Python and run gunicorn with your app.

B) Railway.app (Service)
1) Create new Service from GitHub repository
2) Add a Secret File
- Add your service account JSON under a path such as /workspace/service-account.json (Railway uses different storage; check latest docs)
3) Environment
- Set FIREBASE_CREDENTIALS_PATH=/workspace/service-account.json
- Railway will provide PORT automatically
4) Start command
- gunicorn NemoApp.backend.wsgi:app --workers 2 --threads 8 --timeout 120 --bind 0.0.0.0:$PORT

C) Firebase Admin key notes
- Do not commit the JSON to your repo. Keep it out of Git.
- Use platform secret-storage and point FIREBASE_CREDENTIALS_PATH to that location.
- If the path is wrong, you will see:
  - FileNotFoundError: Firebase service account key not found at ...

D) Health check
- After deploy, hit:
  - GET / → {"message":"Nemo API is running!","version":"0.1.0"}

E) CORS (Frontend)
- CORS is enabled in [python.create_app()](NemoApp/backend/app.py:6)
- If needed, add your production frontend URL to the allowed origins.

F) Troubleshooting
- 502 / 503 on platform
  - Check logs; often the service account path is wrong or worker crashed.
- Import errors
  - Ensure service starts from repo root and module path NemoApp.backend.wsgi resolves.
- Timeouts on heavy endpoints
  - Increase gunicorn workers/threads; consider adding caching if needed.