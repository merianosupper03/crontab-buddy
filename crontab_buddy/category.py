"""Category management for cron expressions."""
import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "categories.json"


def _load(path: Path = _DEFAULT_PATH) -> Dict[str, List[str]]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict[str, List[str]], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_to_category(category: str, expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Add an expression to a category. Returns False if already present."""
    data = _load(path)
    key = category.lower()
    if key not in data:
        data[key] = []
    if expression in data[key]:
        return False
    data[key].append(expression)
    _save(data, path)
    return True


def remove_from_category(category: str, expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove an expression from a category. Returns False if not found."""
    data = _load(path)
    key = category.lower()
    if key not in data or expression not in data[key]:
        return False
    data[key].remove(expression)
    if not data[key]:
        del data[key]
    _save(data, path)
    return True


def get_category(category: str, path: Path = _DEFAULT_PATH) -> List[str]:
    """Return all expressions in a category."""
    data = _load(path)
    return data.get(category.lower(), [])


def list_categories(path: Path = _DEFAULT_PATH) -> List[str]:
    """Return all category names."""
    return sorted(_load(path).keys())


def delete_category(category: str, path: Path = _DEFAULT_PATH) -> bool:
    """Delete an entire category. Returns False if not found."""
    data = _load(path)
    key = category.lower()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True
