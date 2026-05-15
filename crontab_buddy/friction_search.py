"""Search history and favorites by friction score/grade."""
from __future__ import annotations
from typing import Optional
from crontab_buddy.friction import assess_friction
from crontab_buddy.humanizer import humanize
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(expression)
    except Exception:
        return "(unknown)"


def search_history_by_friction(
    min_score: float = 0.0,
    max_score: float = 1.0,
    grade: Optional[str] = None,
) -> list[dict]:
    results = []
    seen: set[str] = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if not expr or expr in seen:
            continue
        seen.add(expr)
        r = assess_friction(expr)
        if r.error:
            continue
        if not (min_score <= r.score <= max_score):
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
    return results


def search_favorites_by_friction(
    min_score: float = 0.0,
    max_score: float = 1.0,
    grade: Optional[str] = None,
) -> list[dict]:
    results = []
    for name, expr in list_favorites():
        r = assess_friction(expr)
        if r.error:
            continue
        if not (min_score <= r.score <= max_score):
            continue
        if grade and r.grade != grade:
            continue
        results.append({
            "expression": expr,
            "description": _safe_humanize(expr),
            "score": r.score,
            "grade": r.grade,
            "name": name,
            "source": "favorites",
        })
    return results
