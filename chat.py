from flask import Blueprint, request, jsonify
from backend.services.llm_service import ask_llm
from backend.services.session_store import handle_message
from backend.routes.auth import require_auth
from backend.utils.helpers import json_success, json_error

chat_bp = Blueprint("chat_bp", __name__, url_prefix="/api/chat")


@chat_bp.post("/")
def chat():
    payload, err = require_auth()
    if err:
        return err

    body    = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()

    if not message:
        return jsonify(json_error("'message' is required."))

    # Use authenticated user_id as session key — stable across requests
    session_id = str(payload["sub"])
    user_id    = int(payload["sub"])

    reply, handled = handle_message(session_id, message, user_id=user_id)
    if handled:
        return jsonify(json_success({"reply": reply}))

    ai_reply = ask_llm(message)
    return jsonify(json_success({"reply": ai_reply}))
