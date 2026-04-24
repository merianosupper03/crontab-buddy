"""Concurrency policy management for cron expressions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_DATA_FILE = Path.home() / ".crontab_buddy" / "concurrency.json"

VALID_POLICIES = ("allow", "skip", "queue", "kill")


def _load() -> Dict:
    if _DATA_FILE.exists():
        return json.loads(_DATA_FILE.read_text())
    return {}


def _save(data: Dict) -> None:
    _DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    _DATA_FILE.write_text(json.dumps(data, indent=2))


def set_concurrency(expression: str, policy: str, max_instances: int = 1) -> None:
    """Set the concurrency policy for a cron expression."""
    if policy not in VALID_POLICIES:
        raise ValueError(f"Invalid policy '{policy}'. Must be one of: {', '.join(VALID_POLICIES)}")
    if max_instances < 1:
        raise ValueError("max_instances must be at least 1")
    data = _load()
    data[expression] = {"policy": policy, "max_instances": max_instances}
    _save(data)


def get_concurrency(expression: str) -> Optional[Dict]:
    """Retrieve the concurrency policy for a cron expression."""
    return _load().get(expression)


def delete_concurrency(expression: str) -> bool:
    """Remove the concurrency policy for a cron expression."""
    data = _load()
    if expression not in data:
        return False
    del data[expression]
    _save(data)
    return True


def list_concurrency() -> Dict:
    """Return all concurrency policies."""
    return _load()
