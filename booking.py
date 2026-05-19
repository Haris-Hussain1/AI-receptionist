from flask import Blueprint, request, jsonify
from backend.database.db import get_connection
from backend.routes.auth import require_auth
from backend.utils.helpers import json_success, json_error

booking_bp = Blueprint("booking_bp", __name__, url_prefix="/api/booking")


@booking_bp.post("/")
def create_booking():
    payload, err = require_auth()
    if err:
        return err

    body   = request.get_json(silent=True) or {}
    name   = body.get("name", "").strip()
    date   = body.get("date", "").strip()
    time   = body.get("time", "").strip()

    if not name or not date or not time:
        return jsonify(json_error("'name', 'date', and 'time' are required."))

    email   = body.get("email", "").strip()
    reason  = body.get("reason", "").strip()
    user_id = int(payload["sub"])

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO appointments (user_id, user_name, user_email, date, time, reason) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, name, email, date, time, reason),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()

    return jsonify(json_success({
        "id": row_id, "user_id": user_id,
        "name": name, "email": email,
        "date": date, "time": time, "reason": reason,
    })), 201


@booking_bp.get("/")
def list_bookings():
    payload, err = require_auth()
    if err:
        return err

    user_id = int(payload["sub"])
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "SELECT id, user_name AS name, user_email AS email, date, time, reason "
        "FROM appointments WHERE user_id = ? ORDER BY id DESC LIMIT 20",
        (user_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(json_success(rows))
