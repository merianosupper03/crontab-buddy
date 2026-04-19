"""Ordered playlist of cron expressions that can be run in sequence."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "playlists.json"


def _load(path: Path = _DEFAULT_PATH) -> Dict[str, List[str]]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict[str, List[str]], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def create_playlist(name: str, path: Path = _DEFAULT_PATH) -> bool:
    """Create an empty playlist. Returns False if already exists."""
    data = _load(path)
    key = name.lower()
    if key in data:
        return False
    data[key] = []
    _save(data, path)
    return True


def add_to_playlist(name: str, expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Append expression to playlist. Returns False if playlist not found."""
    data = _load(path)
    key = name.lower()
    if key not in data:
        return False
    if expression not in data[key]:
        data[key].append(expression)
        _save(data, path)
    return True


def remove_from_playlist(name: str, expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove expression from playlist. Returns False if not found."""
    data = _load(path)
    key = name.lower()
    if key not in data or expression not in data[key]:
        return False
    data[key].remove(expression)
    _save(data, path)
    return True


def get_playlist(name: str, path: Path = _DEFAULT_PATH) -> Optional[List[str]]:
    data = _load(path)
    return data.get(name.lower())


def delete_playlist(name: str, path: Path = _DEFAULT_PATH) -> bool:
    data = _load(path)
    key = name.lower()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True


def list_playlists(path: Path = _DEFAULT_PATH) -> List[str]:
    return list(_load(path).keys())
