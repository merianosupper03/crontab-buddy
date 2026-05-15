"""Search history and favorites by cadence score."""

from __future__ import annotations

from typing import List, Dict, Any, Optional

from crontab_buddy.cadence_score import compute_cadence_score
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid)"


def search_history_by_cadence_score(
    min_score: float = 0.0,
    max_score: float = 1.0,
    grade: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return history entries whose cadence score falls within the given range."""
    results: List[Dict[str, Any]] = []
    seen = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = compute_cadence_score(expr)
        if r.error:
            continue
        if not (min_score <= r.score <= max_score):
            continue
        if grade and r.grade != grade.upper():
            continue
        results.append({
            "expression": expr,
            "description": _safe_humanize(expr),
            "score": r.score,
            "grade": r.grade,
            "source": "history",
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)


def search_favorites_by_cadence_score(
    min_score: float = 0.0,
    max_score: float = 1.0,
    grade: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return favorites whose cadence score falls within the given range."""
    results: List[Dict[str, Any]] = []
    for name, expr in list_favorites():
        r = compute_cadence_score(expr)
        if r.error:
            continue
        if not (min_score <= r.score <= max_score):
            continue
        if grade and r.grade != grade.upper():
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
