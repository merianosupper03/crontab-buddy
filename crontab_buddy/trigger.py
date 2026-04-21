"""Trigger conditions for cron expressions — store and retrieve named trigger rules."""

import json
import os
from typing import Optional

VALID_EVENTS = {"success", "failure", "always", "manual", "dependency"}

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_triggers.json")


def _load(path: str) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_trigger(
    expression: str,
    event: str,
    condition: Optional[str] = None,
    path: str = _DEFAULT_PATH,
) -> None:
    """Attach a trigger rule to a cron expression."""
    if event not in VALID_EVENTS:
        raise ValueError(f"Invalid event '{event}'. Must be one of: {sorted(VALID_EVENTS)}")
    data = _load(path)
    data[expression] = {"event": event, "condition": condition}
    _save(data, path)


def get_trigger(expression: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Return the trigger rule for an expression, or None."""
    return _load(path).get(expression)


def delete_trigger(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove the trigger rule for an expression. Returns True if removed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_triggers(path: str = _DEFAULT_PATH) -> list:
    """Return all stored trigger rules as a list of dicts."""
    data = _load(path)
    return [
        {"expression": expr, **rule}
        for expr, rule in data.items()
    ]
