"""Escalation policy management for cron expressions."""

import json
import os
from typing import Optional

VALID_LEVELS = ("low", "medium", "high", "critical")
VALID_CHANNELS = ("email", "slack", "pagerduty", "webhook", "sms")

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy/escalations.json")


def _load(path: str = _DEFAULT_PATH) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def _save(data: dict, path: str = _DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_escalation(
    expression: str,
    level: str,
    channel: str,
    contact: str,
    path: str = _DEFAULT_PATH,
) -> None:
    """Set an escalation policy for a cron expression."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid level '{level}'. Choose from: {VALID_LEVELS}")
    if channel not in VALID_CHANNELS:
        raise ValueError(f"Invalid channel '{channel}'. Choose from: {VALID_CHANNELS}")
    if not contact.strip():
        raise ValueError("Contact must not be empty.")
    data = _load(path)
    data[expression] = {"level": level, "channel": channel, "contact": contact}
    _save(data, path)


def get_escalation(expression: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Return the escalation policy for an expression, or None."""
    return _load(path).get(expression)


def delete_escalation(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete the escalation policy for an expression. Returns True if deleted."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_escalations(path: str = _DEFAULT_PATH) -> dict:
    """Return all escalation policies."""
    return _load(path)
