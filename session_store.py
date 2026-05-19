import re
from backend.models.appointment import Appointment
from backend.services.booking_service import create_appointment

sessions: dict = {}

# Phrases that clearly signal booking intent — full phrase match, not single words
TRIGGER_PHRASES = {"book appointment", "book an appointment", "schedule appointment",
                   "make appointment", "i want to book", "i'd like to book",
                   "book a slot", "set appointment"}

CANCEL_WORDS = {"no", "cancel", "stop", "exit", "quit", "nevermind", "never mind"}
NEGATION_WORDS = {"not", "don't", "dont", "no", "never", "without", "cancel", "stop"}


def _is_cancel(text: str) -> bool:
    return text.lower().strip() in CANCEL_WORDS


def _has_negation(text: str) -> bool:
    return any(word in text.lower().split() for word in NEGATION_WORDS)


def handle_message(session_id: str, message: str, user_id: int = None) -> tuple[str | None, bool]:
    text  = message.strip()
    lower = text.lower()

    # ── Trigger: only fire on clear booking intent, no negation ─────────────
    if session_id not in sessions and any(phrase in lower for phrase in TRIGGER_PHRASES) and not _has_negation(text):
        sessions[session_id] = {"step": "ask_name", "user_id": user_id}
        return "Of course. Could I get your name please?", True

    session = sessions.get(session_id)
    if not session:
        return None, False

    # ── Cancel escape at any step ─────────────────────────────────────────────
    if _is_cancel(text):
        sessions.pop(session_id, None)
        return "Understood. Please let us know if there is anything else we can assist you with.", True

    step = session["step"]

    # ── Step 1: collect name ──────────────────────────────────────────────────
    if step == "ask_name":
        session["name"] = text
        session["step"] = "ask_date"
        return f"Thank you, {text}. What date would you prefer? (e.g. 2025-08-20)", True

    # ── Step 2: collect date ──────────────────────────────────────────────────
    if step == "ask_date":
        clean_date = re.sub(r'^(on|for|at)\s+', '', text, flags=re.IGNORECASE).strip()
        session["date"] = clean_date
        session["step"] = "confirm"
        return (
            f"Please confirm your appointment details — Name: {session['name']}, Date: {clean_date}. "
            "Reply 'yes' to confirm or 'no' to cancel."
        ), True

    # ── Step 3: confirm and save ──────────────────────────────────────────────
    if step == "confirm":
        if lower in {"yes", "y", "confirm", "ok", "sure", "yep", "yeah"}:
            try:
                saved = create_appointment(Appointment(
                    id=None,
                    user_id=session.get("user_id"),
                    user_name=session["name"],
                    user_email=None,
                    date=session["date"],
                    time="09:00",
                    reason="Booked via chat",
                ))
                reply = f"Your appointment has been confirmed for {saved.date}. We look forward to seeing you."
            except Exception:
                reply = "Sorry, I couldn't save the booking. Please use the booking form."
        else:
            reply = "Booking cancelled. Please let us know if you need any further assistance."

        sessions.pop(session_id, None)
        return reply, True

    return None, False
