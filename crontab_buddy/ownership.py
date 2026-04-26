"""Ownership tracking for cron expressions."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_ownership.json")


def _load(path: str = _DEFAULT_PATH) -> Dict[str, Dict]:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def _save(data: Dict[str, Dict], path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_owner(
    expression: str,
    owner: str,
    team: Optional[str] = None,
    email: Optional[str] = None,
    path: str = _DEFAULT_PATH,
) -> None:
    """Assign an owner to a cron expression."""
    data = _load(path)
    data[expression] = {
        "owner": owner,
        "team": team,
        "email": email,
    }
    _save(data, path)


def get_owner(expression: str, path: str = _DEFAULT_PATH) -> Optional[Dict]:
    """Return ownership info for the given expression, or None."""
    return _load(path).get(expression)


def delete_owner(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove ownership record. Returns True if it existed."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_owners(path: str = _DEFAULT_PATH) -> List[Dict]:
    """Return all ownership records as a list of dicts."""
    data = _load(path)
    return [
        {"expression": expr, **info}
        for expr, info in data.items()
    ]


def find_by_owner(owner: str, path: str = _DEFAULT_PATH) -> List[Dict]:
    """Return all expressions owned by a given owner (case-insensitive)."""
    owner_lower = owner.lower()
    return [
        {"expression": expr, **info}
        for expr, info in _load(path).items()
        if info.get("owner", "").lower() == owner_lower
    ]


def find_by_team(team: str, path: str = _DEFAULT_PATH) -> List[Dict]:
    """Return all expressions belonging to a given team (case-insensitive)."""
    team_lower = team.lower()
    return [
        {"expression": expr, **info}
        for expr, info in _load(path).items()
        if (info.get("team") or "").lower() == team_lower
    ]
