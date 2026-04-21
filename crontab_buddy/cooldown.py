"""Cooldown management: enforce minimum intervals between cron job runs."""

import json
from pathlib import Path
from typing import Optional, Dict

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "cooldowns.json"

VALID_UNITS = {"seconds", "minutes", "hours", "days"}


def _load(path: Path = _DEFAULT_PATH) -> Dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict, path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_cooldown(
    expression: str,
    amount: int,
    unit: str,
    path: Path = _DEFAULT_PATH,
) -> None:
    """Set a cooldown interval for a cron expression."""
    if amount <= 0:
        raise ValueError("Cooldown amount must be a positive integer.")
    unit = unit.lower()
    if unit not in VALID_UNITS:
        raise ValueError(f"Invalid unit '{unit}'. Choose from: {', '.join(sorted(VALID_UNITS))}.")
    data = _load(path)
    data[expression] = {"amount": amount, "unit": unit}
    _save(data, path)


def get_cooldown(expression: str, path: Path = _DEFAULT_PATH) -> Optional[Dict]:
    """Return the cooldown config for an expression, or None."""
    return _load(path).get(expression)


def delete_cooldown(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove a cooldown. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_cooldowns(path: Path = _DEFAULT_PATH) -> Dict:
    """Return all cooldown entries."""
    return _load(path)
