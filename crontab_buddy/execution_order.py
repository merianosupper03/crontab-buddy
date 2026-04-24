"""Manage execution order (priority index) for cron expressions within a named queue."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_execution_order.json")


def _load(path: str = _DEFAULT_PATH) -> Dict[str, List[str]]:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: Dict[str, List[str]], path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_to_queue(queue: str, expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Append expression to queue. Returns False if already present."""
    data = _load(path)
    key = queue.lower()
    entries = data.get(key, [])
    if expression in entries:
        return False
    entries.append(expression)
    data[key] = entries
    _save(data, path)
    return True


def remove_from_queue(queue: str, expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove expression from queue. Returns False if not found."""
    data = _load(path)
    key = queue.lower()
    entries = data.get(key, [])
    if expression not in entries:
        return False
    entries.remove(expression)
    data[key] = entries
    _save(data, path)
    return True


def get_queue(queue: str, path: str = _DEFAULT_PATH) -> List[str]:
    """Return ordered list of expressions for a queue."""
    data = _load(path)
    return data.get(queue.lower(), [])


def move_up(queue: str, expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Move expression one position earlier in the queue."""
    data = _load(path)
    key = queue.lower()
    entries = data.get(key, [])
    if expression not in entries:
        return False
    idx = entries.index(expression)
    if idx == 0:
        return False
    entries[idx - 1], entries[idx] = entries[idx], entries[idx - 1]
    data[key] = entries
    _save(data, path)
    return True


def move_down(queue: str, expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Move expression one position later in the queue."""
    data = _load(path)
    key = queue.lower()
    entries = data.get(key, [])
    if expression not in entries:
        return False
    idx = entries.index(expression)
    if idx == len(entries) - 1:
        return False
    entries[idx], entries[idx + 1] = entries[idx + 1], entries[idx]
    data[key] = entries
    _save(data, path)
    return True


def list_queues(path: str = _DEFAULT_PATH) -> List[str]:
    """Return all queue names."""
    return list(_load(path).keys())


def delete_queue(queue: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete an entire queue. Returns False if not found."""
    data = _load(path)
    key = queue.lower()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True
