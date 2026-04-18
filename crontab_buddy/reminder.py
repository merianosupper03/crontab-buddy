"""Reminder annotations for cron expressions — attach a human note about why a job runs."""

import json
from pathlib import Path
from typing import Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "reminders.json"


def _load(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_reminder(expression: str, message: str, path: Path = _DEFAULT_PATH) -> None:
    """Attach a reminder message to a cron expression string."""
    data = _load(path)
    data[expression] = message.strip()
    _save(data, path)


def get_reminder(expression: str, path: Path = _DEFAULT_PATH) -> Optional[str]:
    """Return the reminder message for an expression, or None."""
    return _load(path).get(expression)


def delete_reminder(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Delete a reminder. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_reminders(path: Path = _DEFAULT_PATH) -> dict:
    """Return all expression -> reminder mappings."""
    return dict(_load(path))
