"""Bookmark module: save and retrieve named bookmarks for cron expressions."""

import json
import os
from typing import Dict, List, Optional

DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_bookmarks.json")


def _load(path: str = DEFAULT_PATH) -> Dict[str, str]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save(data: Dict[str, str], path: str = DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_bookmark(name: str, expression: str, path: str = DEFAULT_PATH) -> bool:
    """Save a bookmark. Returns False if name already exists."""
    data = _load(path)
    if name.lower() in data:
        return False
    data[name.lower()] = expression
    _save(data, path)
    return True


def get_bookmark(name: str, path: str = DEFAULT_PATH) -> Optional[str]:
    """Retrieve expression by bookmark name."""
    return _load(path).get(name.lower())


def delete_bookmark(name: str, path: str = DEFAULT_PATH) -> bool:
    """Delete a bookmark. Returns False if not found."""
    data = _load(path)
    key = name.lower()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True


def list_bookmarks(path: str = DEFAULT_PATH) -> List[Dict[str, str]]:
    """Return all bookmarks as list of dicts with name and expression."""
    data = _load(path)
    return [{"name": k, "expression": v} for k, v in sorted(data.items())]
