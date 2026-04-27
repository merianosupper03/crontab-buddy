"""User feedback storage for cron expressions."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_feedback.json")

VALID_SENTIMENTS = ("positive", "negative", "neutral")


def _load(path: str) -> Dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: Dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_feedback(
    expression: str,
    sentiment: str,
    comment: str = "",
    path: str = _DEFAULT_PATH,
) -> None:
    """Record feedback for a cron expression."""
    if sentiment not in VALID_SENTIMENTS:
        raise ValueError(f"sentiment must be one of {VALID_SENTIMENTS}")
    data = _load(path)
    entries = data.get(expression, [])
    entries.append({
        "sentiment": sentiment,
        "comment": comment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    data[expression] = entries
    _save(data, path)


def get_feedback(expression: str, path: str = _DEFAULT_PATH) -> List[Dict]:
    """Return all feedback entries for a cron expression."""
    return _load(path).get(expression, [])


def delete_feedback(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete all feedback for an expression. Returns True if deleted."""
    data = _load(path)
    if expression not in data:
        return False
    del data[expression]
    _save(data, path)
    return True


def list_all_feedback(path: str = _DEFAULT_PATH) -> Dict[str, List[Dict]]:
    """Return all feedback keyed by expression."""
    return _load(path)


def feedback_summary(expression: str, path: str = _DEFAULT_PATH) -> Dict:
    """Return counts of each sentiment for an expression."""
    entries = get_feedback(expression, path)
    counts: Dict[str, int] = {s: 0 for s in VALID_SENTIMENTS}
    for entry in entries:
        s = entry.get("sentiment", "")
        if s in counts:
            counts[s] += 1
    counts["total"] = len(entries)
    return counts
