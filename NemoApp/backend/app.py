from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Allow frontend local origins during development
    CORS(app, origins=['http://localhost:8080', 'http://localhost:3000'])

    # Register blueprints (implemented in backend/api/)
    try:
        from api.auth import auth_bp
        from api.events import events_bp
        from api.bookings import bookings_bp
        from api.profile import profile_bp
        from api.friends import friends_bp
        from api.admin import admin_bp
        from api.suggestions import suggestions_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(events_bp)
        app.register_blueprint(bookings_bp)
        app.register_blueprint(profile_bp)
        app.register_blueprint(friends_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(suggestions_bp)
    except Exception:
        # Blueprints may not exist yet during initial scaffolding.
        # Import errors are silenced so the app can still start for incremental development.
        pass

    @app.route('/')
    def index():
        return {
            'message': 'Nemo API is running!',
            'version': '0.1.0'
        }

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)