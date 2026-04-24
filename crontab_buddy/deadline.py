"""Deadline tracking for cron expressions."""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "deadlines.json"


def _load(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_deadline(
    expression: str,
    deadline: str,
    note: str = "",
    path: Path = _DEFAULT_PATH,
) -> None:
    """Set a deadline for a cron expression. deadline must be ISO format."""
    try:
        datetime.fromisoformat(deadline)
    except ValueError:
        raise ValueError(f"Invalid deadline format: {deadline!r}. Use ISO 8601.")
    data = _load(path)
    data[expression] = {"deadline": deadline, "note": note}
    _save(data, path)


def get_deadline(expression: str, path: Path = _DEFAULT_PATH) -> Optional[dict]:
    """Return deadline info for expression, or None if not set."""
    return _load(path).get(expression)


def delete_deadline(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove deadline for expression. Returns True if it existed."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_deadlines(path: Path = _DEFAULT_PATH) -> list[dict]:
    """Return all deadlines sorted by deadline datetime ascending."""
    data = _load(path)
    results = []
    for expr, info in data.items():
        results.append({"expression": expr, **info})
    results.sort(key=lambda r: r["deadline"])
    return results


def is_overdue(expression: str, path: Path = _DEFAULT_PATH) -> Optional[bool]:
    """Return True if deadline has passed, False if not, None if no deadline."""
    info = get_deadline(expression, path)
    if info is None:
        return None
    return datetime.now() > datetime.fromisoformat(info["deadline"])
