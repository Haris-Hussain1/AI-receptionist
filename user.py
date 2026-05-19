from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """
    Simple in-memory representation of a user.

    For this demo we only persist a subset of fields in SQLite.
    """

    id: Optional[int]
    name: str
    email: Optional[str] = None

