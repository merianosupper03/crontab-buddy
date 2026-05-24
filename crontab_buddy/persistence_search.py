"""Search history and favorites by persistence grade or score."""
from __future__ import annotations
from typing import Optional
from crontab_buddy.persistence import assess_persistence
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(expression)
    except (CronParseError, Exception):
        return "(invalid)"


def search_history_by_persistence(
    min_score: float = 0.0,
    grade: Optional[str] = None,
) -> list[dict]:
    """Return history entries whose persistence score meets the criteria."""
    results = []
    seen: set[str] = set()
    for entry in get_history():
        expr = entry if isinstance(entry, str) else entry.get("expression", "")
        if not expr or expr in seen:
            continue
        seen.add(expr)
        r = assess_persistence(expr)
        if r.error:
            continue
        if r.score < min_score:
            continue
        if grade and r.grade != grade:
            continue
        results.append({
            "expression": expr,
            "description": _safe_humanize(expr),
            "score": r.score,
            "grade": r.grade,
            "source": "history",
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)


def search_favorites_by_persistence(
    min_score: float = 0.0,
    grade: Optional[str] = None,
) -> list[dict]:
    """Return favorites whose persistence score meets the criteria."""
    results = []
    for name, expr in list_favorites():
        r = assess_persistence(expr)
        if r.error:
            continue
        if r.score < min_score:
            continue
        if grade and r.grade != grade:
            continue
        results.append({
            "name": name,
            "expression": expr,
            "description": _safe_humanize(expr),
            "score": r.score,
            "grade": r.grade,
            "source": "favorites",
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)


def search_above_score(threshold: float) -> list[dict]:
    """Combine history and favorites, returning entries above threshold."""
    hist = search_history_by_persistence(min_score=threshold)
    favs = search_favorites_by_persistence(min_score=threshold)
    seen: set[str] = set()
    combined = []
    for item in hist + favs:
        if item["expression"] not in seen:
            seen.add(item["expression"])
            combined.append(item)
    return sorted(combined, key=lambda x: x["score"], reverse=True)
