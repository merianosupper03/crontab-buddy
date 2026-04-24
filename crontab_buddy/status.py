"""Track and retrieve per-expression status (active, inactive, error)."""

import json
import os
from typing import Optional

VALID_STATUSES = {"active", "inactive", "error"}
_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_status.json")


def _load(path: str = _DEFAULT_PATH) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_status(expression: str, status: str, path: str = _DEFAULT_PATH) -> None:
    """Set the status for a cron expression."""
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
        )
    data = _load(path)
    data[expression] = status
    _save(data, path)


def get_status(expression: str, path: str = _DEFAULT_PATH) -> Optional[str]:
    """Return the status for a cron expression, or None if not set."""
    return _load(path).get(expression)


def delete_status(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove the status entry for an expression. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_statuses(path: str = _DEFAULT_PATH) -> dict:
    """Return all expression -> status mappings."""
    return dict(_load(path))


def filter_by_status(status: str, path: str = _DEFAULT_PATH) -> list:
    """Return all expressions that have the given status."""
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
        )
    data = _load(path)
    return [expr for expr, s in data.items() if s == status]
