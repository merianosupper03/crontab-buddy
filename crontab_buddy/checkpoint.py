"""Checkpoint module: save and restore named checkpoints for cron expressions."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_checkpoints.json")


def _load(path: str = _DEFAULT_PATH) -> Dict:
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _save(data: Dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_checkpoint(name: str, expression: str, note: str = "", path: str = _DEFAULT_PATH) -> None:
    """Save a named checkpoint for the given cron expression."""
    data = _load(path)
    data[name.lower()] = {
        "expression": expression,
        "note": note,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    _save(data, path)


def get_checkpoint(name: str, path: str = _DEFAULT_PATH) -> Optional[Dict]:
    """Retrieve a checkpoint by name, or None if not found."""
    data = _load(path)
    return data.get(name.lower())


def delete_checkpoint(name: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete a checkpoint. Returns True if it existed."""
    data = _load(path)
    key = name.lower()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True


def list_checkpoints(path: str = _DEFAULT_PATH) -> List[Dict]:
    """Return all checkpoints as a list of dicts with 'name' included."""
    data = _load(path)
    return [{"name": k, **v} for k, v in sorted(data.items())]


def search_checkpoints(query: str, path: str = _DEFAULT_PATH) -> List[Dict]:
    """Search checkpoints by name, expression, or note."""
    q = query.lower()
    return [
        cp for cp in list_checkpoints(path)
        if q in cp["name"]
        or q in cp["expression"].lower()
        or q in cp.get("note", "").lower()
    ]
