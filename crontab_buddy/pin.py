"""Pin/unpin cron expressions for quick access."""
import json
from pathlib import Path
from typing import List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "pins.json"


def _load(path: Path) -> List[str]:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, ValueError):
            return []
    return []


def _save(pins: List[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pins, indent=2))


def pin_expression(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Pin an expression. Returns False if already pinned."""
    pins = _load(path)
    if expression in pins:
        return False
    pins.append(expression)
    _save(pins, path)
    return True


def unpin_expression(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    """Unpin an expression. Returns False if not found."""
    pins = _load(path)
    if expression not in pins:
        return False
    pins.remove(expression)
    _save(pins, path)
    return True


def get_pins(path: Path = _DEFAULT_PATH) -> List[str]:
    """Return all pinned expressions."""
    return _load(path)


def is_pinned(expression: str, path: Path = _DEFAULT_PATH) -> bool:
    return expression in _load(path)


def clear_pins(path: Path = _DEFAULT_PATH) -> None:
    _save([], path)
