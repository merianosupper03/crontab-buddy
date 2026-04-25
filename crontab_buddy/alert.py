"""Alert configuration for cron expressions."""
from __future__ import annotations
import json
import os
from typing import Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_alerts.json")

VALID_CHANNELS = {"email", "slack", "pagerduty", "webhook", "log"}
VALID_EVENTS = {"success", "failure", "timeout", "any"}


def _load(path: str = _DEFAULT_PATH) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_alert(
    expression: str,
    channel: str,
    event: str = "failure",
    target: Optional[str] = None,
    path: str = _DEFAULT_PATH,
) -> None:
    """Set an alert for a cron expression."""
    if channel not in VALID_CHANNELS:
        raise ValueError(f"Invalid channel '{channel}'. Choose from: {sorted(VALID_CHANNELS)}")
    if event not in VALID_EVENTS:
        raise ValueError(f"Invalid event '{event}'. Choose from: {sorted(VALID_EVENTS)}")
    data = _load(path)
    data[expression] = {"channel": channel, "event": event, "target": target}
    _save(data, path)


def get_alert(expression: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Retrieve alert config for an expression."""
    return _load(path).get(expression)


def delete_alert(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete alert config for an expression. Returns True if deleted."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_alerts(path: str = _DEFAULT_PATH) -> dict:
    """Return all alert configurations."""
    return _load(path)
