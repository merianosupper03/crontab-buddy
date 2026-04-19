"""Simple expression rating/scoring module."""

import json
import os
from typing import Dict, Optional

DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_ratings.json")


def _load(path: str = DEFAULT_PATH) -> Dict[str, int]:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: Dict[str, int], path: str = DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def rate_expression(expression: str, score: int, path: str = DEFAULT_PATH) -> None:
    """Rate a cron expression with a score from 1 to 5."""
    if not 1 <= score <= 5:
        raise ValueError(f"Score must be between 1 and 5, got {score}")
    data = _load(path)
    data[expression] = score
    _save(data, path)


def get_rating(expression: str, path: str = DEFAULT_PATH) -> Optional[int]:
    """Return the rating for an expression, or None if not rated."""
    return _load(path).get(expression)


def delete_rating(expression: str, path: str = DEFAULT_PATH) -> bool:
    """Remove a rating. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_ratings(path: str = DEFAULT_PATH) -> Dict[str, int]:
    """Return all rated expressions sorted by score descending."""
    data = _load(path)
    return dict(sorted(data.items(), key=lambda x: x[1], reverse=True))


def top_rated(n: int = 5, path: str = DEFAULT_PATH) -> Dict[str, int]:
    """Return the top-n rated expressions."""
    return dict(list(list_ratings(path).items())[:n])
