from dataclasses import dataclass
from typing import Optional


@dataclass
class Appointment:
    """
    Lightweight appointment model used by the booking service
    and Flask routes to pass structured data around.
    """

    id: Optional[int]
    user_id: Optional[int]
    user_name: str
    user_email: Optional[str]
    date: str
    time: str
    reason: Optional[str] = None

