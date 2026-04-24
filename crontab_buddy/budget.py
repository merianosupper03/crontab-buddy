"""Budget module: track and enforce run-count budgets per cron expression."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_budgets.json")

VALID_PERIODS = ("hourly", "daily", "weekly", "monthly")


def _load(path: str = _DEFAULT_PATH) -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: Dict[str, Any], path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_budget(
    expression: str,
    max_runs: int,
    period: str,
    path: str = _DEFAULT_PATH,
) -> None:
    """Set a run-count budget for *expression*."""
    if max_runs < 1:
        raise ValueError("max_runs must be a positive integer")
    if period not in VALID_PERIODS:
        raise ValueError(f"period must be one of {VALID_PERIODS}")
    data = _load(path)
    data[expression] = {"max_runs": max_runs, "period": period}
    _save(data, path)


def get_budget(expression: str, path: str = _DEFAULT_PATH) -> Optional[Dict[str, Any]]:
    """Return the budget entry for *expression*, or None."""
    return _load(path).get(expression)


def delete_budget(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete the budget for *expression*. Returns True if it existed."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_budgets(path: str = _DEFAULT_PATH) -> List[Dict[str, Any]]:
    """Return all budget entries as a list of dicts."""
    data = _load(path)
    return [
        {"expression": expr, **info}
        for expr, info in data.items()
    ]
