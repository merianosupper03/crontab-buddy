"""Lifecycle management for cron expressions (draft -> active -> deprecated -> retired)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

_DATA_FILE = os.path.expanduser("~/.crontab_buddy_lifecycle.json")

VALID_STATES = ["draft", "active", "deprecated", "retired"]


def _load() -> Dict:
    if os.path.exists(_DATA_FILE):
        with open(_DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def _save(data: Dict) -> None:
    with open(_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_lifecycle(expression: str, state: str, reason: Optional[str] = None) -> None:
    """Set the lifecycle state of a cron expression."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state '{state}'. Must be one of: {VALID_STATES}")
    data = _load()
    prev = data.get(expression, {}).get("state")
    data[expression] = {
        "state": state,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "previous_state": prev,
    }
    _save(data)


def get_lifecycle(expression: str) -> Optional[Dict]:
    """Return lifecycle info for an expression, or None if not set."""
    return _load().get(expression)


def delete_lifecycle(expression: str) -> bool:
    """Remove lifecycle info. Returns True if it existed."""
    data = _load()
    if expression in data:
        del data[expression]
        _save(data)
        return True
    return False


def list_by_state(state: str) -> List[Dict]:
    """Return all expressions in a given lifecycle state."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state '{state}'. Must be one of: {VALID_STATES}")
    data = _load()
    return [
        {"expression": expr, **info}
        for expr, info in data.items()
        if info.get("state") == state
    ]


def list_all_lifecycles() -> List[Dict]:
    """Return all expressions with their lifecycle info."""
    data = _load()
    return [{"expression": expr, **info} for expr, info in data.items()]
