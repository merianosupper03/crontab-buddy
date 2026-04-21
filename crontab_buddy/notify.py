"""Notification settings for cron expressions."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

_DEFAULT_PATH = os.path.join(
    os.path.expanduser("~"), ".crontab_buddy", "notify.json"
)

VALID_EVENTS = ("success", "failure", "always")


def _load(path: str = _DEFAULT_PATH) -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path, "r") as fh:
            return json.load(fh)
    return {}


def _save(data: Dict[str, Any], path: str = _DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def set_notify(
    expression: str,
    email: str,
    event: str = "failure",
    path: str = _DEFAULT_PATH,
) -> None:
    """Attach an email notification to a cron expression."""
    if event not in VALID_EVENTS:
        raise ValueError(
            f"Invalid event '{event}'. Choose from: {', '.join(VALID_EVENTS)}"
        )
    data = _load(path)
    data[expression] = {"email": email, "event": event}
    _save(data, path)


def get_notify(
    expression: str, path: str = _DEFAULT_PATH
) -> Optional[Dict[str, str]]:
    """Return notification config for an expression, or None."""
    return _load(path).get(expression)


def delete_notify(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove notification config. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_notify(path: str = _DEFAULT_PATH) -> List[Dict[str, str]]:
    """Return all notification configs as a list of dicts."""
    data = _load(path)
    return [
        {"expression": expr, **cfg} for expr, cfg in data.items()
    ]
