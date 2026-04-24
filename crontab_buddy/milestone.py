"""Track milestones (run count targets) for cron expressions."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_milestones.json")


def _load(path: str = _DEFAULT_PATH) -> Dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: Dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_milestone(expression: str, name: str, target: int, path: str = _DEFAULT_PATH) -> None:
    """Create or update a named milestone for an expression."""
    if target < 1:
        raise ValueError("target must be a positive integer")
    data = _load(path)
    key = expression.strip()
    if key not in data:
        data[key] = {}
    data[key][name] = {"target": target, "reached": False}
    _save(data, path)


def get_milestone(expression: str, name: str, path: str = _DEFAULT_PATH) -> Optional[Dict]:
    """Return milestone dict or None if not found."""
    data = _load(path)
    return data.get(expression.strip(), {}).get(name)


def mark_reached(expression: str, name: str, path: str = _DEFAULT_PATH) -> bool:
    """Mark a milestone as reached. Returns True if it existed and was updated."""
    data = _load(path)
    key = expression.strip()
    if key in data and name in data[key]:
        data[key][name]["reached"] = True
        _save(data, path)
        return True
    return False


def delete_milestone(expression: str, name: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete a milestone. Returns True if it existed."""
    data = _load(path)
    key = expression.strip()
    if key in data and name in data[key]:
        del data[key][name]
        if not data[key]:
            del data[key]
        _save(data, path)
        return True
    return False


def list_milestones(expression: str, path: str = _DEFAULT_PATH) -> List[Dict]:
    """Return all milestones for an expression as a list of dicts."""
    data = _load(path)
    entries = data.get(expression.strip(), {})
    return [
        {"name": n, "target": v["target"], "reached": v["reached"]}
        for n, v in entries.items()
    ]
