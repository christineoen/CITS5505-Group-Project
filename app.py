from flask import Flask
from config import Config
from database import close_db, init_db
from routes.main import main_bp
from routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Set up database connection teardown
    app.teardown_appcontext(close_db)

    # Initialize database tables
    with app.app_context():
        init_db()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5001, use_reloader=False)
