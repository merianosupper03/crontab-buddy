"""Named schedules: save and retrieve cron expressions by a friendly name."""

import json
from pathlib import Path
from typing import Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "schedule_names.json"


def _load(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def save_schedule(name: str, expression: str, description: str = "", path: Path = _DEFAULT_PATH) -> None:
    """Save a named schedule."""
    data = _load(path)
    data[name.lower()] = {"expression": expression, "description": description}
    _save(data, path)


def get_schedule(name: str, path: Path = _DEFAULT_PATH) -> Optional[dict]:
    """Retrieve a named schedule or None if not found."""
    data = _load(path)
    return data.get(name.lower())


def delete_schedule(name: str, path: Path = _DEFAULT_PATH) -> bool:
    """Delete a named schedule. Returns True if it existed."""
    data = _load(path)
    key = name.lower()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True


def list_schedules(path: Path = _DEFAULT_PATH) -> dict:
    """Return all named schedules."""
    return _load(path)
