"""Suppression: temporarily suppress a cron expression from running."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Optional

_DEFAULT_PATH = os.path.join(
    os.path.expanduser("~"), ".crontab_buddy", "suppressions.json"
)


def _load(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def suppress_expression(
    expression: str,
    reason: Optional[str] = None,
    until: Optional[str] = None,
    path: str = _DEFAULT_PATH,
) -> bool:
    """Suppress an expression. Returns False if already suppressed."""
    data = _load(path)
    if expression in data:
        return False
    data[expression] = {
        "suppressed_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "until": until,
    }
    _save(data, path)
    return True


def unsuppress_expression(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove suppression. Returns False if not suppressed."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def is_suppressed(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Return True if the expression is currently suppressed."""
    data = _load(path)
    return expression in data


def get_suppression(expression: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Return suppression details or None."""
    return _load(path).get(expression)


def list_suppressions(path: str = _DEFAULT_PATH) -> dict:
    """Return all suppressed expressions."""
    return _load(path)


def clear_suppressions(path: str = _DEFAULT_PATH) -> int:
    """Remove all suppressions. Returns count cleared."""
    data = _load(path)
    count = len(data)
    _save({}, path)
    return count
