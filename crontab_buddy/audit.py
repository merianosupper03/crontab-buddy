"""Audit log: track actions performed on cron expressions."""

import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DEFAULT_AUDIT_FILE = os.path.expanduser("~/.crontab_buddy_audit.json")


def _load(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save(entries: List[Dict[str, Any]], path: str) -> None:
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def log_action(
    action: str,
    expression: str,
    detail: Optional[str] = None,
    path: str = DEFAULT_AUDIT_FILE,
) -> None:
    """Append an audit entry for the given action and expression."""
    entries = _load(path)
    entry: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "expression": expression,
    }
    if detail:
        entry["detail"] = detail
    entries.append(entry)
    _save(entries, path)


def get_audit_log(
    action_filter: Optional[str] = None,
    path: str = DEFAULT_AUDIT_FILE,
) -> List[Dict[str, Any]]:
    """Return audit entries, optionally filtered by action type."""
    entries = _load(path)
    if action_filter:
        entries = [e for e in entries if e.get("action") == action_filter]
    return entries


def clear_audit_log(path: str = DEFAULT_AUDIT_FILE) -> None:
    """Remove all audit log entries."""
    _save([], path)
