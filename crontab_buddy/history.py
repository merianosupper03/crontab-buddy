"""Persist and retrieve recently used cron expressions."""

import json
import os
from pathlib import Path
from typing import List, Optional

DEFAULT_HISTORY_FILE = Path.home() / ".crontab_buddy_history.json"
MAX_HISTORY = 50


def _load(path: Path) -> List[dict]:
    if not path.exists():
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save(entries: List[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def add_entry(expression: str, comment: Optional[str] = None,
              path: Path = DEFAULT_HISTORY_FILE) -> None:
    """Add a cron expression to history, avoiding consecutive duplicates."""
    entries = _load(path)
    entry = {"expression": expression, "comment": comment or ""}
    if entries and entries[-1]["expression"] == expression:
        return
    entries.append(entry)
    if len(entries) > MAX_HISTORY:
        entries = entries[-MAX_HISTORY:]
    _save(entries, path)


def get_history(path: Path = DEFAULT_HISTORY_FILE) -> List[dict]:
    """Return all history entries, most recent last."""
    return _load(path)


def clear_history(path: Path = DEFAULT_HISTORY_FILE) -> None:
    """Wipe the history file."""
    if path.exists():
        path.unlink()


def search_history(keyword: str,
                   path: Path = DEFAULT_HISTORY_FILE) -> List[dict]:
    """Return entries whose expression or comment contains keyword."""
    keyword = keyword.lower()
    return [
        e for e in _load(path)
        if keyword in e["expression"].lower() or keyword in e["comment"].lower()
    ]
