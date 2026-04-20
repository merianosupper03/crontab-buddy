"""Priority management for cron expressions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "priorities.json"

VALID_LEVELS = ("low", "medium", "high", "critical")


def _load(path: Path = _DEFAULT_PATH) -> Dict[str, str]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict[str, str], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_priority(expression: str, level: str, path: Path = _DEFAULT_PATH) -> None:
    """Assign a priority level to a cron expression."""
    level = level.lower()
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid priority level '{level}'. Choose from: {', '.join(VALID_LEVELS)}")
    data = _load(path)
    data[expression] = level
    _save(data, path)


def get_priority(expression: str, path: Path = _DEFAULT_PATH) -> Optional[str]:
    """Return the priority level for a cron expression, or None if not set."""
    return _load(path).get(expression)


def delete_priority(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove priority for an expression. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_priorities(path: Path = _DEFAULT_PATH) -> List[Dict[str, str]]:
    """Return all expressions with their priority levels, sorted by level severity."""
    data = _load(path)
    order = {level: i for i, level in enumerate(reversed(VALID_LEVELS))}
    entries = [
        {"expression": expr, "priority": level}
        for expr, level in data.items()
    ]
    entries.sort(key=lambda e: order.get(e["priority"], 99))
    return entries


def filter_by_priority(level: str, path: Path = _DEFAULT_PATH) -> List[str]:
    """Return all expressions that match a given priority level."""
    level = level.lower()
    return [expr for expr, lvl in _load(path).items() if lvl == level]
