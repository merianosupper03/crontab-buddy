"""Visibility settings for cron expressions (public/private/team)."""

import json
import os
from typing import Dict, List, Optional

_FILE = os.path.expanduser("~/.crontab_buddy_visibility.json")

VALID_LEVELS = ("public", "private", "team")


def _load() -> Dict:
    if os.path.exists(_FILE):
        with open(_FILE, "r") as f:
            return json.load(f)
    return {}


def _save(data: Dict) -> None:
    with open(_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_visibility(expression: str, level: str, team: Optional[str] = None) -> None:
    """Set visibility level for a cron expression."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid visibility level '{level}'. Must be one of: {VALID_LEVELS}")
    if level == "team" and not team:
        raise ValueError("A team name is required when visibility is 'team'")
    data = _load()
    entry = {"level": level}
    if team:
        entry["team"] = team
    data[expression] = entry
    _save(data)


def get_visibility(expression: str) -> Optional[Dict]:
    """Get visibility settings for a cron expression."""
    return _load().get(expression)


def delete_visibility(expression: str) -> bool:
    """Remove visibility settings for a cron expression."""
    data = _load()
    if expression not in data:
        return False
    del data[expression]
    _save(data)
    return True


def list_visibility() -> List[Dict]:
    """Return all visibility entries as a list of dicts."""
    data = _load()
    return [
        {"expression": expr, **entry}
        for expr, entry in data.items()
    ]


def filter_by_level(level: str) -> List[str]:
    """Return all expressions with the given visibility level."""
    return [
        expr for expr, entry in _load().items()
        if entry.get("level") == level
    ]
