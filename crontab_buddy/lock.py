"""Per-expression execution lock management.

Allows marking an expression as locked (preventing edits or runs)
and querying / clearing lock state.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "locks.json"


def _load(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def lock_expression(
    expression: str,
    reason: str = "",
    path: Path = _DEFAULT_PATH,
) -> bool:
    """Lock an expression. Returns False if already locked."""
    data = _load(path)
    if expression in data:
        return False
    data[expression] = {
        "reason": reason,
        "locked_at": datetime.now(timezone.utc).isoformat(),
    }
    _save(data, path)
    return True


def unlock_expression(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Unlock an expression. Returns False if not locked."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def get_lock(expression: str, path: Path = _DEFAULT_PATH) -> Optional[dict]:
    """Return lock info dict or None if not locked."""
    return _load(path).get(expression)


def is_locked(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Return True if the expression is currently locked."""
    return expression in _load(path)


def list_locks(path: Path = _DEFAULT_PATH) -> dict:
    """Return all locked expressions and their lock metadata."""
    return dict(_load(path))


def clear_locks(path: Path = _DEFAULT_PATH) -> int:
    """Remove all locks. Returns the number of locks cleared."""
    data = _load(path)
    count = len(data)
    _save({}, path)
    return count
