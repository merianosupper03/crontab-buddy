"""Archive (soft-delete) expressions with optional reason."""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from typing import Optional

_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".crontab_buddy_archive.json")


def _load(path: str) -> list:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


def _save(data: list, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def archive_expression(expression: str, reason: str = "", path: str = _DEFAULT_PATH) -> dict:
    entries = _load(path)
    entry = {
        "expression": expression,
        "reason": reason,
        "archived_at": datetime.now(timezone.utc).isoformat(),
    }
    entries.append(entry)
    _save(entries, path)
    return entry


def get_archive(path: str = _DEFAULT_PATH) -> list:
    return _load(path)


def delete_from_archive(expression: str, path: str = _DEFAULT_PATH) -> bool:
    entries = _load(path)
    new = [e for e in entries if e["expression"] != expression]
    if len(new) == len(entries):
        return False
    _save(new, path)
    return True


def clear_archive(path: str = _DEFAULT_PATH) -> None:
    _save([], path)


def search_archive(keyword: str, path: str = _DEFAULT_PATH) -> list:
    keyword = keyword.lower()
    return [
        e for e in _load(path)
        if keyword in e["expression"].lower() or keyword in e.get("reason", "").lower()
    ]
