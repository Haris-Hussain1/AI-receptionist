"""
Utility helpers that are shared across the backend.

This module currently contains small convenience functions for
formatting and validation, and is intended to grow as needed.
"""

from typing import Any, Dict


def json_error(message: str) -> Dict[str, Any]:
    return {"success": False, "error": message}


def json_success(data: Any) -> Dict[str, Any]:
    """
    Wrap arbitrary data in a consistent success envelope.
    """
    return {"success": True, "data": data}

