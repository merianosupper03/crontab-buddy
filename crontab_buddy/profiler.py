"""Profiler: track and report execution time estimates for cron expressions."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_profiler.json")


def _load(path: str = _DEFAULT_PATH) -> Dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: Dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_profile(
    expression: str,
    avg_seconds: float,
    max_seconds: Optional[float] = None,
    notes: str = "",
    path: str = _DEFAULT_PATH,
) -> None:
    """Store execution time profile for a cron expression."""
    if avg_seconds < 0:
        raise ValueError("avg_seconds must be non-negative")
    if max_seconds is not None and max_seconds < avg_seconds:
        raise ValueError("max_seconds must be >= avg_seconds")
    data = _load(path)
    data[expression] = {
        "avg_seconds": avg_seconds,
        "max_seconds": max_seconds,
        "notes": notes,
    }
    _save(data, path)


def get_profile(expression: str, path: str = _DEFAULT_PATH) -> Optional[Dict]:
    """Retrieve execution profile for a cron expression, or None if not set."""
    return _load(path).get(expression)


def delete_profile(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete a profile entry. Returns True if deleted, False if not found."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_profiles(path: str = _DEFAULT_PATH) -> List[Dict]:
    """Return all profiles with expression and description."""
    data = _load(path)
    results = []
    for expr, profile in data.items():
        try:
            desc = humanize(CronExpression(expr))
        except (CronParseError, Exception):
            desc = "(invalid expression)"
        results.append({"expression": expr, "description": desc, **profile})
    return results
