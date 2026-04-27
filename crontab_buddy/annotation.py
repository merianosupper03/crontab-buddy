"""Annotation module: attach free-form annotations to cron expressions."""

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "annotations.json"


def _load(path: Path = _DEFAULT_PATH) -> Dict[str, List[Dict]]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict, path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def add_annotation(
    expression: str,
    text: str,
    author: Optional[str] = None,
    path: Path = _DEFAULT_PATH,
) -> Dict:
    """Add an annotation to an expression. Returns the new annotation entry."""
    if not text.strip():
        raise ValueError("Annotation text must not be empty.")
    data = _load(path)
    key = expression.strip()
    entry = {"text": text.strip(), "author": author}
    data.setdefault(key, []).append(entry)
    _save(data, path)
    return entry


def get_annotations(
    expression: str, path: Path = _DEFAULT_PATH
) -> List[Dict]:
    """Return all annotations for the given expression."""
    data = _load(path)
    return data.get(expression.strip(), [])


def delete_annotation(
    expression: str, index: int, path: Path = _DEFAULT_PATH
) -> bool:
    """Delete annotation by index. Returns True if deleted, False if not found."""
    data = _load(path)
    key = expression.strip()
    entries = data.get(key, [])
    if index < 0 or index >= len(entries):
        return False
    entries.pop(index)
    if not entries:
        data.pop(key, None)
    else:
        data[key] = entries
    _save(data, path)
    return True


def clear_annotations(expression: str, path: Path = _DEFAULT_PATH) -> int:
    """Remove all annotations for an expression. Returns count removed."""
    data = _load(path)
    key = expression.strip()
    removed = len(data.pop(key, []))
    _save(data, path)
    return removed


def list_all_annotations(path: Path = _DEFAULT_PATH) -> Dict[str, List[Dict]]:
    """Return all annotations across all expressions."""
    return _load(path)
