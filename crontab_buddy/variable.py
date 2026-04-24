"""Variable substitution for cron expressions.

Allows storing named variables (e.g. EVERY_HOUR = "0 * * * *") and
expanding them by name when building or validating expressions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "variables.json"


def _load(path: Path = _DEFAULT_PATH) -> Dict[str, str]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict[str, str], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_variable(name: str, expression: str, path: Path = _DEFAULT_PATH) -> None:
    """Store a named variable mapping to a cron expression string."""
    data = _load(path)
    data[name.upper()] = expression
    _save(data, path)


def get_variable(name: str, path: Path = _DEFAULT_PATH) -> Optional[str]:
    """Retrieve a cron expression by variable name (case-insensitive)."""
    return _load(path).get(name.upper())


def delete_variable(name: str, path: Path = _DEFAULT_PATH) -> bool:
    """Delete a variable. Returns True if it existed, False otherwise."""
    data = _load(path)
    key = name.upper()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True


def list_variables(path: Path = _DEFAULT_PATH) -> List[Dict[str, str]]:
    """Return all variables as a list of {name, expression} dicts."""
    data = _load(path)
    return [{"name": k, "expression": v} for k, v in sorted(data.items())]


def expand_variable(name: str, path: Path = _DEFAULT_PATH) -> Optional[str]:
    """Expand a variable name to its expression, or None if not found."""
    return get_variable(name, path)
