"""Run log: record and retrieve execution logs for cron expressions."""

import json
import os
from datetime import datetime
from typing import Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_runlog.json")


def _load(path: str) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def log_run(
    expression: str,
    status: str,
    message: str = "",
    path: str = _DEFAULT_PATH,
) -> dict:
    """Append a run entry for the given expression. Status should be 'ok' or 'fail'."""
    if status not in ("ok", "fail"):
        raise ValueError(f"status must be 'ok' or 'fail', got {status!r}")
    data = _load(path)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
        "message": message,
    }
    data.setdefault(expression, []).append(entry)
    _save(data, path)
    return entry


def get_runs(
    expression: str,
    path: str = _DEFAULT_PATH,
    limit: Optional[int] = None,
) -> list:
    """Return run log entries for the given expression, newest first."""
    data = _load(path)
    entries = list(reversed(data.get(expression, [])))
    if limit is not None:
        entries = entries[:limit]
    return entries


def clear_runs(expression: str, path: str = _DEFAULT_PATH) -> None:
    """Remove all run log entries for the given expression."""
    data = _load(path)
    data.pop(expression, None)
    _save(data, path)


def list_all_runs(path: str = _DEFAULT_PATH) -> dict:
    """Return the full run log keyed by expression."""
    return _load(path)
