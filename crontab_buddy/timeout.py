"""Timeout configuration for cron expressions."""
from __future__ import annotations

import json
import os
from typing import Dict, Optional

_DEFAULT_PATH = os.path.join(
    os.path.expanduser("~"), ".crontab_buddy", "timeouts.json"
)


def _load(path: str = _DEFAULT_PATH) -> Dict[str, dict]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save(data: Dict[str, dict], path: str = _DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_timeout(
    expression: str,
    seconds: int,
    action: str = "kill",
    path: str = _DEFAULT_PATH,
) -> None:
    """Set a timeout for a cron expression.

    Args:
        expression: The cron expression string.
        seconds: Maximum allowed runtime in seconds (must be > 0).
        action: What to do on timeout — 'kill' or 'notify'.
        path: Storage file path.
    """
    if seconds <= 0:
        raise ValueError("seconds must be a positive integer")
    if action not in ("kill", "notify"):
        raise ValueError("action must be 'kill' or 'notify'")
    data = _load(path)
    data[expression] = {"seconds": seconds, "action": action}
    _save(data, path)


def get_timeout(expression: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Return timeout config for the given expression, or None."""
    return _load(path).get(expression)


def delete_timeout(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove timeout config. Returns True if it existed."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_timeouts(path: str = _DEFAULT_PATH) -> Dict[str, dict]:
    """Return all stored timeout configurations."""
    return dict(_load(path))
