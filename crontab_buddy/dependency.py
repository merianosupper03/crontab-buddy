"""Dependency tracking between named schedules."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "dependencies.json"


def _load(path: Path = _DEFAULT_PATH) -> Dict[str, List[str]]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict[str, List[str]], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_dependency(schedule: str, depends_on: str, path: Path = _DEFAULT_PATH) -> bool:
    """Record that *schedule* depends on *depends_on*. Returns False if already present."""
    data = _load(path)
    key = schedule.lower()
    deps = data.setdefault(key, [])
    if depends_on.lower() in deps:
        return False
    deps.append(depends_on.lower())
    _save(data, path)
    return True


def remove_dependency(schedule: str, depends_on: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove a dependency. Returns False if it did not exist."""
    data = _load(path)
    key = schedule.lower()
    deps = data.get(key, [])
    dep = depends_on.lower()
    if dep not in deps:
        return False
    deps.remove(dep)
    if not deps:
        del data[key]
    else:
        data[key] = deps
    _save(data, path)
    return True


def get_dependencies(schedule: str, path: Path = _DEFAULT_PATH) -> List[str]:
    """Return all dependencies for *schedule*."""
    data = _load(path)
    return list(data.get(schedule.lower(), []))


def list_all_dependencies(path: Path = _DEFAULT_PATH) -> Dict[str, List[str]]:
    """Return the full dependency map."""
    return dict(_load(path))


def clear_dependencies(schedule: str, path: Path = _DEFAULT_PATH) -> None:
    """Remove all dependencies for *schedule*."""
    data = _load(path)
    data.pop(schedule.lower(), None)
    _save(data, path)
