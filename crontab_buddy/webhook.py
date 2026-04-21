"""Webhook notification settings for cron expressions."""

import json
import os
from typing import Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_webhooks.json")


def _load(path: str = _DEFAULT_PATH) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_webhook(
    expression: str,
    url: str,
    on_success: bool = True,
    on_failure: bool = True,
    path: str = _DEFAULT_PATH,
) -> None:
    """Register a webhook URL for a cron expression."""
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid webhook URL: {url!r}")
    data = _load(path)
    data[expression] = {
        "url": url,
        "on_success": on_success,
        "on_failure": on_failure,
    }
    _save(data, path)


def get_webhook(expression: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Return webhook config for an expression, or None."""
    return _load(path).get(expression)


def delete_webhook(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove webhook config. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_webhooks(path: str = _DEFAULT_PATH) -> dict:
    """Return all webhook registrations."""
    return dict(_load(path))
