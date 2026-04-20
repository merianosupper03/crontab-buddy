"""Attach arbitrary key-value metadata to cron expressions."""

import json
import os
from typing import Any, Dict, Optional

_DEFAULT_PATH = os.path.join(
    os.path.expanduser("~"), ".crontab_buddy", "metadata.json"
)


def _load(path: str = _DEFAULT_PATH) -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save(data: Dict[str, Dict[str, Any]], path: str = _DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_metadata(expression: str, key: str, value: Any, path: str = _DEFAULT_PATH) -> None:
    """Set a metadata key for the given cron expression."""
    data = _load(path)
    if expression not in data:
        data[expression] = {}
    data[expression][key] = value
    _save(data, path)


def get_metadata(expression: str, key: str, path: str = _DEFAULT_PATH) -> Optional[Any]:
    """Return the metadata value for a key, or None if not set."""
    data = _load(path)
    return data.get(expression, {}).get(key)


def get_all_metadata(expression: str, path: str = _DEFAULT_PATH) -> Dict[str, Any]:
    """Return all metadata for the given expression."""
    data = _load(path)
    return dict(data.get(expression, {}))


def delete_metadata(expression: str, key: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete a single metadata key. Returns True if it existed."""
    data = _load(path)
    if expression in data and key in data[expression]:
        del data[expression][key]
        if not data[expression]:
            del data[expression]
        _save(data, path)
        return True
    return False


def clear_metadata(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove all metadata for an expression. Returns True if anything was removed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_all_metadata(path: str = _DEFAULT_PATH) -> Dict[str, Dict[str, Any]]:
    """Return the full metadata store."""
    return _load(path)
