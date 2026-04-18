"""Snapshot: save and restore named snapshots of cron expressions with metadata."""

import json
import os
from datetime import datetime
from typing import Optional

DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_snapshots.json")


def _load(path: str = DEFAULT_PATH) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str = DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_snapshot(name: str, expression: str, comment: str = "", path: str = DEFAULT_PATH) -> None:
    """Save a named snapshot of a cron expression."""
    data = _load(path)
    data[name] = {
        "expression": expression,
        "comment": comment,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
    }
    _save(data, path)


def get_snapshot(name: str, path: str = DEFAULT_PATH) -> Optional[dict]:
    """Retrieve a snapshot by name, or None if not found."""
    return _load(path).get(name)


def delete_snapshot(name: str, path: str = DEFAULT_PATH) -> bool:
    """Delete a snapshot. Returns True if it existed."""
    data = _load(path)
    if name in data:
        del data[name]
        _save(data, path)
        return True
    return False


def list_snapshots(path: str = DEFAULT_PATH) -> list:
    """Return all snapshots as a list of dicts with 'name' included."""
    data = _load(path)
    return [{"name": k, **v} for k, v in data.items()]
