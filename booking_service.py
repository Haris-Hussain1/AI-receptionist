"""
Service layer for creating and listing appointments.

This keeps database interactions in one place so the Flask routes
can remain slim and focused on HTTP concerns.
"""

from typing import List

from backend.database.db import get_connection
from backend.models.appointment import Appointment


def create_appointment(appointment: Appointment) -> Appointment:
    """
    Persist a new appointment and return it with an assigned ID.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO appointments (user_id, user_name, user_email, date, time, reason)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            appointment.user_id,
            appointment.user_name,
            appointment.user_email,
            appointment.date,
            appointment.time,
            appointment.reason,
        ),
    )

    appointment.id = cur.lastrowid
    conn.commit()
    conn.close()
    return appointment


def list_appointments(limit: int = 20) -> List[Appointment]:
    """
    Return the most recent appointments up to the given limit.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, user_name, user_email, date, time, reason
        FROM appointments
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cur.fetchall()
    conn.close()

    return [
        Appointment(
            id=row["id"],
            user_name=row["user_name"],
            user_email=row["user_email"],
            date=row["date"],
            time=row["time"],
            reason=row["reason"],
        )
        for row in rows
    ]

