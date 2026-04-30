"""SLA (Service Level Agreement) tracking for cron expressions."""

from __future__ import annotations

import json
import os
from typing import Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_sla.json")

VALID_POLICIES = ("strict", "relaxed", "best-effort")


def _load(path: str = _DEFAULT_PATH) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_sla(
    expression: str,
    max_duration_seconds: int,
    policy: str = "strict",
    note: Optional[str] = None,
    path: str = _DEFAULT_PATH,
) -> dict:
    """Set an SLA for a cron expression."""
    if max_duration_seconds <= 0:
        raise ValueError("max_duration_seconds must be a positive integer")
    if policy not in VALID_POLICIES:
        raise ValueError(f"policy must be one of {VALID_POLICIES}")
    data = _load(path)
    entry = {
        "max_duration_seconds": max_duration_seconds,
        "policy": policy,
    }
    if note:
        entry["note"] = note
    data[expression] = entry
    _save(data, path)
    return entry


def get_sla(expression: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Return the SLA entry for an expression, or None."""
    return _load(path).get(expression)


def delete_sla(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete an SLA entry. Returns True if it existed."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_slas(path: str = _DEFAULT_PATH) -> dict:
    """Return all SLA entries."""
    return _load(path)


def check_sla(expression: str, actual_seconds: int, path: str = _DEFAULT_PATH) -> dict:
    """Check whether actual_seconds violates the SLA. Returns a result dict."""
    entry = get_sla(expression, path)
    if entry is None:
        return {"expression": expression, "status": "no_sla", "violated": False}
    violated = actual_seconds > entry["max_duration_seconds"]
    return {
        "expression": expression,
        "max_duration_seconds": entry["max_duration_seconds"],
        "actual_seconds": actual_seconds,
        "policy": entry["policy"],
        "violated": violated,
        "status": "violated" if violated else "ok",
    }
