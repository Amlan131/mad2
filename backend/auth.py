from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models import User
from passlib.hash import bcrypt
import jwt
from functools import wraps
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)


def create_token(user):
    payload = {
        "sub": user.id,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    token = jwt.encode(
        payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token


def require_auth(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"error": "missing token"}), 401
            token = auth.split(" ")[1]
            try:
                data = jwt.decode(
                    token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            except Exception:
                return jsonify({"error": "invalid token"}), 401
            user = User.query.get(data["sub"])
            if not user:
                return jsonify({"error": "user not found"}), 401
            if role and user.role != role:
                return jsonify({"error": "forbidden"}), 403
            request.user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@auth_bp.post("/register")
def register():
    data = request.json or {}
    if not data.get("username") or not data.get("password"):
        return {"error": "username/password required"}, 400
    if User.query.filter((User.username == data["username"]) | (User.email == data.get("email"))).first():
        return {"error": "user exists"}, 400
    u = User(username=data["username"], email=data.get(
        "email"), password_hash=bcrypt.hash(data["password"]), role="user")
    db.session.add(u)
    db.session.commit()
    return {"message": "registered"}, 201


@auth_bp.post("/login")
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    u = User.query.filter_by(username=username).first()
    if not u or not bcrypt.verify(password, u.password_hash):
        return {"error": "invalid credentials"}, 401
    return {"token": create_token(u), "role": u.role, "username": u.username}
