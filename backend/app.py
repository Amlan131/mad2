# app.py
from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, cache
from tasks import make_celery
from auth import auth_bp
from admin import admin_bp
from user import user_bp
from seed import ensure_admin

celery_app = None


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)
    db.init_app(app)
    cache.init_app(app)

    # blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(user_bp, url_prefix="/api/user")

    with app.app_context():
        from models import User, ParkingLot, ParkingSpot, Reservation
        db.create_all()
        ensure_admin()

    global celery_app
    celery_app = make_celery(app)

    @app.route("/api/health")
    def health():
        return {"ok": True}

    return app


app = create_app()
