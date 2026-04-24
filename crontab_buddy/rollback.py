"""Rollback support: save and restore expression snapshots per named slot."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_rollback.json")


def _load(path: str = _DEFAULT_PATH) -> Dict[str, List[dict]]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save(data: Dict[str, List[dict]], path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def push_rollback(name: str, expression: str, path: str = _DEFAULT_PATH) -> None:
    """Push the current expression onto the rollback stack for a named slot."""
    data = _load(path)
    stack = data.get(name, [])
    stack.append({"expression": expression, "timestamp": datetime.utcnow().isoformat()})
    data[name] = stack
    _save(data, path)


def pop_rollback(name: str, path: str = _DEFAULT_PATH) -> Optional[str]:
    """Pop the most recent expression from the rollback stack. Returns None if empty."""
    data = _load(path)
    stack = data.get(name, [])
    if not stack:
        return None
    entry = stack.pop()
    data[name] = stack
    _save(data, path)
    return entry["expression"]


def peek_rollback(name: str, path: str = _DEFAULT_PATH) -> Optional[str]:
    """Peek at the most recent expression without removing it."""
    data = _load(path)
    stack = data.get(name, [])
    if not stack:
        return None
    return stack[-1]["expression"]


def get_rollback_stack(name: str, path: str = _DEFAULT_PATH) -> List[dict]:
    """Return the full rollback stack for a named slot."""
    data = _load(path)
    return list(data.get(name, []))


def clear_rollback(name: str, path: str = _DEFAULT_PATH) -> bool:
    """Clear the rollback stack for a named slot. Returns True if it existed."""
    data = _load(path)
    if name not in data:
        return False
    del data[name]
    _save(data, path)
    return True


def list_rollback_slots(path: str = _DEFAULT_PATH) -> List[str]:
    """List all named rollback slots."""
    return list(_load(path).keys())
