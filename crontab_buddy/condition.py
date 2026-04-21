"""Conditional execution rules attached to cron expressions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DATA_FILE = Path.home() / ".crontab_buddy" / "conditions.json"

VALID_OPERATORS = ("==", "!=", ">", ">=", "<", "<=", "contains", "not_contains")


def _load() -> Dict[str, List[dict]]:
    if not _DATA_FILE.exists():
        return {}
    try:
        return json.loads(_DATA_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: Dict[str, List[dict]]) -> None:
    _DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    _DATA_FILE.write_text(json.dumps(data, indent=2))


def add_condition(
    expression: str,
    variable: str,
    operator: str,
    value: str,
    *,
    data_file: Path = _DATA_FILE,
) -> bool:
    """Add a condition rule for the given cron expression. Returns False if duplicate."""
    if operator not in VALID_OPERATORS:
        raise ValueError(f"Invalid operator '{operator}'. Valid: {VALID_OPERATORS}")
    global _DATA_FILE
    _DATA_FILE = data_file
    data = _load()
    conditions = data.setdefault(expression, [])
    rule = {"variable": variable, "operator": operator, "value": value}
    if rule in conditions:
        return False
    conditions.append(rule)
    _save(data)
    return True


def get_conditions(expression: str, *, data_file: Path = _DATA_FILE) -> List[dict]:
    """Return all conditions for the given expression."""
    global _DATA_FILE
    _DATA_FILE = data_file
    return _load().get(expression, [])


def remove_condition(
    expression: str,
    variable: str,
    operator: str,
    value: str,
    *,
    data_file: Path = _DATA_FILE,
) -> bool:
    """Remove a specific condition. Returns False if not found."""
    global _DATA_FILE
    _DATA_FILE = data_file
    data = _load()
    conditions = data.get(expression, [])
    rule = {"variable": variable, "operator": operator, "value": value}
    if rule not in conditions:
        return False
    conditions.remove(rule)
    if not conditions:
        data.pop(expression, None)
    else:
        data[expression] = conditions
    _save(data)
    return True


def clear_conditions(expression: str, *, data_file: Path = _DATA_FILE) -> int:
    """Remove all conditions for an expression. Returns count removed."""
    global _DATA_FILE
    _DATA_FILE = data_file
    data = _load()
    removed = len(data.pop(expression, []))
    _save(data)
    return removed


def list_all_conditions(*, data_file: Path = _DATA_FILE) -> Dict[str, List[dict]]:
    """Return all conditions across all expressions."""
    global _DATA_FILE
    _DATA_FILE = data_file
    return dict(_load())
