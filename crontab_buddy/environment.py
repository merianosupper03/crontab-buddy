"""Manage environment variable associations for cron expressions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "environments.json"


def _load(path: Path = _DEFAULT_PATH) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_env_var(expression: str, key: str, value: str, path: Path = _DEFAULT_PATH) -> None:
    """Set an environment variable for a cron expression."""
    data = _load(path)
    if expression not in data:
        data[expression] = {}
    data[expression][key.upper()] = value
    _save(data, path)


def get_env_var(expression: str, key: str, path: Path = _DEFAULT_PATH) -> Optional[str]:
    """Get a specific environment variable for a cron expression."""
    data = _load(path)
    return data.get(expression, {}).get(key.upper())


def get_all_env_vars(expression: str, path: Path = _DEFAULT_PATH) -> Dict[str, str]:
    """Return all environment variables associated with a cron expression."""
    data = _load(path)
    return dict(data.get(expression, {}))


def delete_env_var(expression: str, key: str, path: Path = _DEFAULT_PATH) -> bool:
    """Delete a specific environment variable. Returns True if deleted."""
    data = _load(path)
    env = data.get(expression, {})
    if key.upper() in env:
        del env[key.upper()]
        data[expression] = env
        _save(data, path)
        return True
    return False


def clear_env_vars(expression: str, path: Path = _DEFAULT_PATH) -> None:
    """Remove all environment variables for a cron expression."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)


def list_all_env_vars(path: Path = _DEFAULT_PATH) -> Dict[str, Dict[str, str]]:
    """Return all stored environment variable mappings."""
    return _load(path)
