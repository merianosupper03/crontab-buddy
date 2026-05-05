"""Heartbeat tracking for cron expressions."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "heartbeats.json"


def _load(path: Path = _DEFAULT_PATH) -> Dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict, path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def record_heartbeat(expression: str, status: str = "ok", path: Path = _DEFAULT_PATH) -> None:
    """Record a heartbeat ping for the given expression."""
    valid_statuses = {"ok", "warn", "fail"}
    if status not in valid_statuses:
        raise ValueError(f"status must be one of {valid_statuses}")
    data = _load(path)
    entry = {
        "timestamp": time.time(),
        "status": status,
    }
    data.setdefault(expression, []).append(entry)
    _save(data, path)


def get_heartbeats(expression: str, path: Path = _DEFAULT_PATH) -> List[Dict]:
    """Return all heartbeat records for an expression, newest first."""
    data = _load(path)
    entries = data.get(expression, [])
    return sorted(entries, key=lambda e: e["timestamp"], reverse=True)


def latest_heartbeat(expression: str, path: Path = _DEFAULT_PATH) -> Optional[Dict]:
    """Return the most recent heartbeat for an expression, or None."""
    records = get_heartbeats(expression, path)
    return records[0] if records else None


def clear_heartbeats(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove all heartbeat records for an expression."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_heartbeats(path: Path = _DEFAULT_PATH) -> Dict[str, List[Dict]]:
    """Return all heartbeat data keyed by expression."""
    return _load(path)
