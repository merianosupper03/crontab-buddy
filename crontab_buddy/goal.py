"""Goal tracking: set a target run count for a cron expression and track progress."""

import json
import os
from typing import Optional

DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_goals.json")


def _load(path: str) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_goal(expression: str, target: int, note: str = "", path: str = DEFAULT_PATH) -> None:
    """Set a run-count goal for a cron expression."""
    if target < 1:
        raise ValueError("Target must be a positive integer.")
    data = _load(path)
    data[expression] = {"target": target, "count": data.get(expression, {}).get("count", 0), "note": note}
    _save(data, path)


def record_run(expression: str, path: str = DEFAULT_PATH) -> int:
    """Increment the run count for an expression. Returns new count."""
    data = _load(path)
    if expression not in data:
        data[expression] = {"target": 0, "count": 0, "note": ""}
    data[expression]["count"] += 1
    _save(data, path)
    return data[expression]["count"]


def get_goal(expression: str, path: str = DEFAULT_PATH) -> Optional[dict]:
    """Return goal dict or None if not set."""
    return _load(path).get(expression)


def delete_goal(expression: str, path: str = DEFAULT_PATH) -> bool:
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_goals(path: str = DEFAULT_PATH) -> list:
    """Return all goals as list of dicts with expression key."""
    data = _load(path)
    return [{"expression": expr, **info} for expr, info in data.items()]


def progress(expression: str, path: str = DEFAULT_PATH) -> Optional[float]:
    """Return completion ratio (0.0-1.0+) or None if no goal set."""
    g = get_goal(expression, path)
    if g is None or g["target"] == 0:
        return None
    return g["count"] / g["target"]
