"""Label management for cron expressions."""
import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "labels.json"


def _load(path: Path = _DEFAULT_PATH) -> Dict[str, List[str]]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict[str, List[str]], path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_label(expression: str, label: str, path: Path = _DEFAULT_PATH) -> bool:
    """Add a label to an expression. Returns False if already labeled."""
    data = _load(path)
    labels = data.setdefault(expression, [])
    if label in labels:
        return False
    labels.append(label)
    _save(data, path)
    return True


def remove_label(expression: str, label: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove a label from an expression. Returns False if not found."""
    data = _load(path)
    labels = data.get(expression, [])
    if label not in labels:
        return False
    labels.remove(label)
    if not labels:
        del data[expression]
    else:
        data[expression] = labels
    _save(data, path)
    return True


def get_labels(expression: str, path: Path = _DEFAULT_PATH) -> List[str]:
    """Return all labels for an expression."""
    return _load(path).get(expression, [])


def find_by_label(label: str, path: Path = _DEFAULT_PATH) -> List[str]:
    """Return all expressions that have the given label."""
    data = _load(path)
    return [expr for expr, labels in data.items() if label in labels]


def list_all_labels(path: Path = _DEFAULT_PATH) -> Dict[str, List[str]]:
    """Return the full label mapping."""
    return _load(path)
