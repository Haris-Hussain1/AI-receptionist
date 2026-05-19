import jwt
import time
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database.db import get_connection
from backend.utils.helpers import json_success, json_error
from backend.config import config

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


def _make_token(user_id: int, email: str) -> str:
    payload = {
        "sub":   str(user_id),
        "email": email,
        "iat":   int(time.time()),
        "exp":   int(time.time()) + 86400 * 7,
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")


def get_current_user():
    """
    Decode the Bearer token from the Authorization header.
    Returns the payload dict or None if missing/invalid.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        return jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def require_auth():
    """Return (payload, None) or (None, error_response)."""
    payload = get_current_user()
    if not payload:
        return None, (jsonify(json_error("Authentication required. Please log in.")), 401)
    return payload, None


@auth_bp.post("/register")
def register():
    body     = request.get_json(silent=True) or {}
    name     = body.get("name", "").strip()
    email    = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not name or not email or not password:
        return jsonify(json_error("Name, email, and password are required.")), 400

    conn = get_connection()
    cur  = conn.cursor()

    if cur.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
        conn.close()
        return jsonify(json_error("An account with that email already exists.")), 409

    cur.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, generate_password_hash(password)),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    return jsonify(json_success({"token": _make_token(user_id, email), "name": name})), 201


@auth_bp.post("/login")
def login():
    body     = request.get_json(silent=True) or {}
    email    = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        return jsonify(json_error("Email and password are required.")), 400

    conn = get_connection()
    row  = conn.execute(
        "SELECT id, name, password_hash FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()

    if not row:
        return jsonify(json_error("No account found with that email. Please register first.")), 404

    if not check_password_hash(row["password_hash"], password):
        return jsonify(json_error("Incorrect password. Please try again.")), 401

    return jsonify(json_success({"token": _make_token(row["id"], email), "name": row["name"]}))
