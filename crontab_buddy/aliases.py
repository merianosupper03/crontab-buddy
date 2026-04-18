"""Named alias management for cron expressions."""

import json
import os
from typing import Dict, Optional

DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_aliases.json")


def _load(path: str = DEFAULT_PATH) -> Dict[str, str]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save(data: Dict[str, str], path: str = DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_alias(name: str, expression: str, path: str = DEFAULT_PATH) -> None:
    """Store a named alias for a cron expression."""
    data = _load(path)
    data[name.lower()] = expression
    _save(data, path)


def get_alias(name: str, path: str = DEFAULT_PATH) -> Optional[str]:
    """Retrieve a cron expression by alias name."""
    return _load(path).get(name.lower())


def delete_alias(name: str, path: str = DEFAULT_PATH) -> bool:
    """Delete an alias. Returns True if it existed."""
    data = _load(path)
    key = name.lower()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True


def list_aliases(path: str = DEFAULT_PATH) -> Dict[str, str]:
    """Return all stored aliases."""
    return _load(path)


def resolve(name_or_expr: str, path: str = DEFAULT_PATH) -> str:
    """Return the expression for an alias, or the input itself if not found."""
    return get_alias(name_or_expr, path) or name_or_expr
