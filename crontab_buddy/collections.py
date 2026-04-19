"""Named collections of cron expressions."""
import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "collections.json"


def _load(path: Path = _DEFAULT_PATH) -> Dict[str, List[str]]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict[str, List[str]], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_to_collection(name: str, expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Add expression to a named collection. Returns False if already present."""
    data = _load(path)
    col = data.setdefault(name.lower(), [])
    if expression in col:
        return False
    col.append(expression)
    _save(data, path)
    return True


def remove_from_collection(name: str, expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove expression from collection. Returns False if not found."""
    data = _load(path)
    col = data.get(name.lower(), [])
    if expression not in col:
        return False
    col.remove(expression)
    data[name.lower()] = col
    _save(data, path)
    return True


def get_collection(name: str, path: Path = _DEFAULT_PATH) -> Optional[List[str]]:
    data = _load(path)
    return data.get(name.lower())


def list_collections(path: Path = _DEFAULT_PATH) -> List[str]:
    return list(_load(path).keys())


def delete_collection(name: str, path: Path = _DEFAULT_PATH) -> bool:
    data = _load(path)
    if name.lower() not in data:
        return False
    del data[name.lower()]
    _save(data, path)
    return True
