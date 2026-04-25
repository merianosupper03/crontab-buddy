"""Expiry management for cron expressions.

Allows setting an expiry date/time after which an expression is considered
stale or should no longer run.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Optional

_FILE = os.path.join(os.path.expanduser("~"), ".crontab_buddy_expiry.json")

DATE_FMT = "%Y-%m-%dT%H:%M:%S"


def _load() -> dict:
    if os.path.exists(_FILE):
        with open(_FILE) as f:
            return json.load(f)
    return {}


def _save(data: dict) -> None:
    with open(_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_expiry(expression: str, expires_at: datetime, reason: str = "") -> None:
    """Set an expiry datetime for a cron expression."""
    data = _load()
    data[expression] = {
        "expires_at": expires_at.strftime(DATE_FMT),
        "reason": reason,
    }
    _save(data)


def get_expiry(expression: str) -> Optional[dict]:
    """Return expiry info for an expression, or None if not set."""
    return _load().get(expression)


def delete_expiry(expression: str) -> bool:
    """Remove expiry for an expression. Returns True if it existed."""
    data = _load()
    if expression in data:
        del data[expression]
        _save(data)
        return True
    return False


def is_expired(expression: str, now: Optional[datetime] = None) -> bool:
    """Return True if the expression has passed its expiry datetime."""
    entry = get_expiry(expression)
    if entry is None:
        return False
    if now is None:
        now = datetime.utcnow()
    expires_at = datetime.strptime(entry["expires_at"], DATE_FMT)
    return now >= expires_at


def list_expiries() -> list[dict]:
    """Return all expiry entries as a list of dicts."""
    data = _load()
    result = []
    for expr, info in data.items():
        result.append({"expression": expr, **info})
    return result
