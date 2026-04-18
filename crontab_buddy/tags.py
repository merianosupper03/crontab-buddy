"""Tagging system for saved cron expressions."""

import json
import os
from typing import Dict, List

DEFAULT_TAGS_FILE = os.path.expanduser("~/.crontab_buddy_tags.json")


def _load(path: str = DEFAULT_TAGS_FILE) -> Dict[str, List[str]]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save(data: Dict[str, List[str]], path: str = DEFAULT_TAGS_FILE) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_tag(expression: str, tag: str, path: str = DEFAULT_TAGS_FILE) -> None:
    """Add a tag to a cron expression."""
    data = _load(path)
    tags = data.setdefault(expression, [])
    if tag not in tags:
        tags.append(tag)
    _save(data, path)


def remove_tag(expression: str, tag: str, path: str = DEFAULT_TAGS_FILE) -> bool:
    """Remove a tag from a cron expression. Returns True if removed."""
    data = _load(path)
    if expression not in data or tag not in data[expression]:
        return False
    data[expression].remove(tag)
    if not data[expression]:
        del data[expression]
    _save(data, path)
    return True


def get_tags(expression: str, path: str = DEFAULT_TAGS_FILE) -> List[str]:
    """Get all tags for a cron expression."""
    data = _load(path)
    return data.get(expression, [])


def find_by_tag(tag: str, path: str = DEFAULT_TAGS_FILE) -> List[str]:
    """Return all expressions that have the given tag."""
    data = _load(path)
    return [expr for expr, tags in data.items() if tag in tags]


def list_all_tags(path: str = DEFAULT_TAGS_FILE) -> Dict[str, List[str]]:
    """Return the full tag mapping."""
    return _load(path)


def clear_tags(path: str = DEFAULT_TAGS_FILE) -> None:
    """Remove all tag data."""
    _save({}, path)
