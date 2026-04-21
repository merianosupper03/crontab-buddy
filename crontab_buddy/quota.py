"""Quota management: limit how many times an expression can run in a period."""

import json
import os
from typing import Optional, Dict, Any

_QUOTA_FILE = os.path.expanduser("~/.crontab_buddy_quota.json")

VALID_PERIODS = ("hourly", "daily", "weekly", "monthly")


def _load() -> Dict[str, Any]:
    if os.path.exists(_QUOTA_FILE):
        with open(_QUOTA_FILE, "r") as f:
            return json.load(f)
    return {}


def _save(data: Dict[str, Any]) -> None:
    with open(_QUOTA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_quota(expression: str, max_runs: int, period: str) -> None:
    """Set a quota for how many times an expression may run in a period."""
    if max_runs < 1:
        raise ValueError("max_runs must be at least 1")
    if period not in VALID_PERIODS:
        raise ValueError(f"period must be one of {VALID_PERIODS}")
    data = _load()
    data[expression] = {"max_runs": max_runs, "period": period}
    _save(data)


def get_quota(expression: str) -> Optional[Dict[str, Any]]:
    """Return the quota config for an expression, or None if not set."""
    return _load().get(expression)


def delete_quota(expression: str) -> bool:
    """Remove quota for an expression. Returns True if it existed."""
    data = _load()
    if expression in data:
        del data[expression]
        _save(data)
        return True
    return False


def list_quotas() -> Dict[str, Any]:
    """Return all quota entries."""
    return _load()
