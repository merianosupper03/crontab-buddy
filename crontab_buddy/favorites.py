"""Save and load named favorite cron expressions."""

import json
from pathlib import Path
from typing import Dict, Optional

DEFAULT_FAVORITES_FILE = Path.home() / ".crontab_buddy_favorites.json"


def _load(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: Dict[str, dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_favorite(name: str, expression: str, comment: str = "",
                  path: Path = DEFAULT_FAVORITES_FILE) -> None:
    """Save or overwrite a named favorite."""
    data = _load(path)
    data[name] = {"expression": expression, "comment": comment}
    _save(data, path)


def get_favorite(name: str, path: Path = DEFAULT_FAVORITES_FILE) -> Optional[dict]:
    """Return a favorite by name, or None if not found."""
    return _load(path).get(name)


def list_favorites(path: Path = DEFAULT_FAVORITES_FILE) -> Dict[str, dict]:
    """Return all saved favorites."""
    return _load(path)


def delete_favorite(name: str, path: Path = DEFAULT_FAVORITES_FILE) -> bool:
    """Delete a favorite by name. Returns True if it existed."""
    data = _load(path)
    if name not in data:
        return False
    del data[name]
    _save(data, path)
    return True
