"""Throttle settings for cron expressions — limit how often a job can run."""

import json
from pathlib import Path
from typing import Optional, Dict, Any

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "throttle.json"

VALID_UNITS = ("seconds", "minutes", "hours", "days")


def _load(path: Path) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_throttle(
    expression: str,
    interval: int,
    unit: str,
    path: Path = _DEFAULT_PATH,
) -> None:
    """Set a throttle for an expression (min interval between runs)."""
    if interval <= 0:
        raise ValueError("interval must be a positive integer")
    if unit not in VALID_UNITS:
        raise ValueError(f"unit must be one of {VALID_UNITS}")
    data = _load(path)
    data[expression] = {"interval": interval, "unit": unit}
    _save(data, path)


def get_throttle(
    expression: str, path: Path = _DEFAULT_PATH
) -> Optional[Dict[str, Any]]:
    """Return throttle config for an expression, or None if not set."""
    return _load(path).get(expression)


def delete_throttle(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove throttle for an expression. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_throttles(path: Path = _DEFAULT_PATH) -> Dict[str, Any]:
    """Return all throttle settings keyed by expression."""
    return _load(path)
