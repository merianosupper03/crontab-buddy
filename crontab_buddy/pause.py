"""Pause/resume support for cron expressions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "paused.json"


def _load(path: Path) -> Dict[str, dict]:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save(data: Dict[str, dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def pause_expression(
    expression: str,
    reason: Optional[str] = None,
    path: Path = _DEFAULT_PATH,
) -> bool:
    """Mark an expression as paused. Returns False if already paused."""
    data = _load(path)
    key = expression.strip()
    if key in data:
        return False
    data[key] = {"reason": reason or ""}
    _save(data, path)
    return True


def resume_expression(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove an expression from the paused set. Returns False if not found."""
    data = _load(path)
    key = expression.strip()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True


def is_paused(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Return True if the expression is currently paused."""
    data = _load(path)
    return expression.strip() in data


def get_pause_info(
    expression: str, path: Path = _DEFAULT_PATH
) -> Optional[dict]:
    """Return pause metadata for an expression, or None if not paused."""
    data = _load(path)
    return data.get(expression.strip())


def list_paused(path: Path = _DEFAULT_PATH) -> Dict[str, dict]:
    """Return all paused expressions with their metadata."""
    return _load(path)


def clear_paused(path: Path = _DEFAULT_PATH) -> None:
    """Remove all paused entries."""
    _save({}, path)
