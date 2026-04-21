"""Execution window constraints for cron expressions.

Allows defining time windows (start/end hour) during which a cron job
is permitted to run.
"""

from __future__ import annotations

import json
import os
from typing import Dict, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_windows.json")


def _load(path: str = _DEFAULT_PATH) -> Dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: Dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_window(
    expression: str,
    start_hour: int,
    end_hour: int,
    path: str = _DEFAULT_PATH,
) -> None:
    """Set an execution window for the given cron expression.

    Args:
        expression: The cron expression string.
        start_hour: Hour (0-23) when the window opens.
        end_hour: Hour (0-23) when the window closes (inclusive).

    Raises:
        ValueError: If hours are out of range or start >= end.
    """
    if not (0 <= start_hour <= 23) or not (0 <= end_hour <= 23):
        raise ValueError("Hours must be between 0 and 23.")
    if start_hour >= end_hour:
        raise ValueError("start_hour must be less than end_hour.")
    data = _load(path)
    data[expression] = {"start_hour": start_hour, "end_hour": end_hour}
    _save(data, path)


def get_window(expression: str, path: str = _DEFAULT_PATH) -> Optional[Dict]:
    """Return the execution window for an expression, or None if not set."""
    return _load(path).get(expression)


def delete_window(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete the execution window for an expression.

    Returns True if deleted, False if not found.
    """
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_windows(path: str = _DEFAULT_PATH) -> Dict:
    """Return all stored execution windows."""
    return dict(_load(path))


def is_within_window(expression: str, hour: int, path: str = _DEFAULT_PATH) -> bool:
    """Check whether *hour* falls within the execution window for *expression*.

    Returns True if no window is defined (unrestricted).
    """
    window = get_window(expression, path)
    if window is None:
        return True
    return window["start_hour"] <= hour <= window["end_hour"]
