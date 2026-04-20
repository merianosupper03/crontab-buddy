"""Retry policy module — attach retry metadata to cron expressions."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

_DEFAULT_PATH = os.path.join(
    os.path.expanduser("~"), ".crontab_buddy", "retry.json"
)

VALID_STRATEGIES = ("fixed", "exponential", "linear")


def _load(path: str = _DEFAULT_PATH) -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _save(data: Dict[str, Any], path: str = _DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_retry(
    expression: str,
    max_attempts: int,
    strategy: str = "fixed",
    delay_seconds: int = 60,
    path: str = _DEFAULT_PATH,
) -> None:
    """Attach a retry policy to a cron expression."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    if strategy not in VALID_STRATEGIES:
        raise ValueError(f"strategy must be one of {VALID_STRATEGIES}")
    if delay_seconds < 0:
        raise ValueError("delay_seconds must be >= 0")
    data = _load(path)
    data[expression] = {
        "max_attempts": max_attempts,
        "strategy": strategy,
        "delay_seconds": delay_seconds,
    }
    _save(data, path)


def get_retry(expression: str, path: str = _DEFAULT_PATH) -> Optional[Dict[str, Any]]:
    """Return retry policy for expression, or None if not set."""
    return _load(path).get(expression)


def delete_retry(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove retry policy. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_retry_policies(path: str = _DEFAULT_PATH) -> List[Dict[str, Any]]:
    """Return all expressions with retry policies attached."""
    data = _load(path)
    return [
        {"expression": expr, **policy}
        for expr, policy in data.items()
    ]
