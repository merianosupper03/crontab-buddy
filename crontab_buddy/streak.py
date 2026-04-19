"""Track how many days in a row a cron expression has been used."""

import json
import os
from datetime import date, timedelta
from typing import Optional

DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_streaks.json")


def _load(path: str) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def record_use(expression: str, path: str = DEFAULT_PATH) -> None:
    """Record that an expression was used today."""
    data = _load(path)
    today = date.today().isoformat()
    entry = data.get(expression, {"last_date": None, "streak": 0, "total": 0})

    last = entry.get("last_date")
    if last == today:
        pass  # already recorded today
    elif last == (date.today() - timedelta(days=1)).isoformat():
        entry["streak"] += 1
    else:
        entry["streak"] = 1

    entry["last_date"] = today
    entry["total"] = entry.get("total", 0) + 1
    data[expression] = entry
    _save(data, path)


def get_streak(expression: str, path: str = DEFAULT_PATH) -> Optional[dict]:
    """Return streak info for an expression, or None if not found."""
    data = _load(path)
    return data.get(expression)


def list_streaks(path: str = DEFAULT_PATH) -> list:
    """Return all streaks sorted by streak count descending."""
    data = _load(path)
    results = []
    for expr, info in data.items():
        results.append({"expression": expr, **info})
    return sorted(results, key=lambda x: x.get("streak", 0), reverse=True)


def reset_streak(expression: str, path: str = DEFAULT_PATH) -> bool:
    """Reset streak for an expression. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False
