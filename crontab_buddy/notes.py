"""Attach and retrieve plain-text notes for cron expressions."""

import json
import os
from typing import Optional

DEFAULT_NOTES_FILE = os.path.expanduser("~/.crontab_buddy_notes.json")


def _load(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_note(expression: str, note: str, path: str = DEFAULT_NOTES_FILE) -> None:
    """Set or overwrite the note for a cron expression."""
    data = _load(path)
    data[expression] = note
    _save(data, path)


def get_note(expression: str, path: str = DEFAULT_NOTES_FILE) -> Optional[str]:
    """Return the note for a cron expression, or None if not set."""
    data = _load(path)
    return data.get(expression)


def delete_note(expression: str, path: str = DEFAULT_NOTES_FILE) -> bool:
    """Delete the note for a cron expression. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_notes(path: str = DEFAULT_NOTES_FILE) -> dict:
    """Return all expression -> note mappings."""
    return _load(path)
