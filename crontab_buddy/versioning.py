"""Expression versioning — store and retrieve named versions of a cron expression."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_versions.json")


def _load(path: str = _DEFAULT_PATH) -> Dict:
    if os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)
    return {}


def _save(data: Dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def save_version(expression: str, version: str, note: str = "", path: str = _DEFAULT_PATH) -> None:
    """Save a named version for *expression*."""
    data = _load(path)
    key = expression.strip()
    if key not in data:
        data[key] = []
    # avoid duplicate version labels for the same expression
    data[key] = [v for v in data[key] if v["version"] != version]
    data[key].append({
        "version": version,
        "note": note,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    })
    _save(data, path)


def get_versions(expression: str, path: str = _DEFAULT_PATH) -> List[Dict]:
    """Return all saved versions for *expression*, oldest first."""
    data = _load(path)
    return list(data.get(expression.strip(), []))


def get_version(expression: str, version: str, path: str = _DEFAULT_PATH) -> Optional[Dict]:
    """Return a specific version entry or *None* if not found."""
    for entry in get_versions(expression, path):
        if entry["version"] == version:
            return entry
    return None


def delete_version(expression: str, version: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete a named version.  Returns *True* if it existed."""
    data = _load(path)
    key = expression.strip()
    before = len(data.get(key, []))
    data[key] = [v for v in data.get(key, []) if v["version"] != version]
    if not data[key]:
        data.pop(key, None)
    _save(data, path)
    return len(data.get(key, [])) < before


def list_all_versions(path: str = _DEFAULT_PATH) -> Dict[str, List[Dict]]:
    """Return the full versioning store."""
    return _load(path)
