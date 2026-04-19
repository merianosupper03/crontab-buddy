"""Group multiple cron expressions under a named group."""

import json
import os
from typing import Dict, List, Optional

DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_groups.json")


def _load(path: str = DEFAULT_PATH) -> Dict[str, List[str]]:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def _save(data: Dict[str, List[str]], path: str = DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def create_group(name: str, path: str = DEFAULT_PATH) -> bool:
    """Create a new empty group. Returns False if already exists."""
    data = _load(path)
    key = name.lower()
    if key in data:
        return False
    data[key] = []
    _save(data, path)
    return True


def add_to_group(name: str, expression: str, path: str = DEFAULT_PATH) -> bool:
    """Add an expression to a group. Returns False if duplicate."""
    data = _load(path)
    key = name.lower()
    if key not in data:
        data[key] = []
    if expression in data[key]:
        return False
    data[key].append(expression)
    _save(data, path)
    return True


def remove_from_group(name: str, expression: str, path: str = DEFAULT_PATH) -> bool:
    """Remove an expression from a group. Returns False if not found."""
    data = _load(path)
    key = name.lower()
    if key not in data or expression not in data[key]:
        return False
    data[key].remove(expression)
    _save(data, path)
    return True


def get_group(name: str, path: str = DEFAULT_PATH) -> Optional[List[str]]:
    """Return list of expressions in a group, or None if group doesn't exist."""
    data = _load(path)
    return data.get(name.lower())


def delete_group(name: str, path: str = DEFAULT_PATH) -> bool:
    """Delete an entire group. Returns False if not found."""
    data = _load(path)
    key = name.lower()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True


def list_groups(path: str = DEFAULT_PATH) -> Dict[str, List[str]]:
    """Return all groups and their expressions."""
    return _load(path)
