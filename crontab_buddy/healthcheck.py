"""Health check configuration for cron expressions."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_healthchecks.json")

VALID_METHODS = ("ping", "heartbeat", "http")


def _load(path: str = _DEFAULT_PATH) -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: Dict[str, Any], path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_healthcheck(
    expression: str,
    url: str,
    method: str = "ping",
    grace_seconds: int = 60,
    path: str = _DEFAULT_PATH,
) -> None:
    """Attach a health check URL to a cron expression."""
    if method not in VALID_METHODS:
        raise ValueError(f"method must be one of {VALID_METHODS}, got {method!r}")
    if grace_seconds < 0:
        raise ValueError("grace_seconds must be non-negative")
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"url must start with http:// or https://, got {url!r}")
    data = _load(path)
    data[expression] = {"url": url, "method": method, "grace_seconds": grace_seconds}
    _save(data, path)


def get_healthcheck(expression: str, path: str = _DEFAULT_PATH) -> Optional[Dict[str, Any]]:
    """Return health check config for an expression, or None."""
    return _load(path).get(expression)


def delete_healthcheck(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove health check for an expression. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_healthchecks(path: str = _DEFAULT_PATH) -> List[Dict[str, Any]]:
    """Return all health checks as a list of dicts with expression key included."""
    data = _load(path)
    return [{"expression": expr, **cfg} for expr, cfg in data.items()]
