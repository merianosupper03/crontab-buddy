"""Capacity management: track max allowed concurrent runs per expression."""

import json
import os
from typing import Optional

DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_capacity.json")

VALID_STRATEGIES = ("drop", "queue", "replace")


def _load(path: str) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_capacity(
    expression: str,
    max_slots: int,
    strategy: str = "drop",
    path: str = DEFAULT_PATH,
) -> None:
    """Set capacity for an expression."""
    if not isinstance(max_slots, int) or max_slots < 1:
        raise ValueError("max_slots must be a positive integer")
    if strategy not in VALID_STRATEGIES:
        raise ValueError(f"strategy must be one of {VALID_STRATEGIES}")
    data = _load(path)
    data[expression] = {"max_slots": max_slots, "strategy": strategy}
    _save(data, path)


def get_capacity(expression: str, path: str = DEFAULT_PATH) -> Optional[dict]:
    """Return capacity config for an expression, or None."""
    return _load(path).get(expression)


def delete_capacity(expression: str, path: str = DEFAULT_PATH) -> bool:
    """Delete capacity config. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_capacities(path: str = DEFAULT_PATH) -> dict:
    """Return all capacity configs keyed by expression."""
    return _load(path)
