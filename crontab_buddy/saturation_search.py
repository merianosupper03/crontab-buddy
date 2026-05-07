"""Search history and favorites by saturation grade."""
from __future__ import annotations
from typing import List, Dict, Any
from crontab_buddy.saturation import assess_saturation
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except (CronParseError, Exception):
        return "(invalid)"


def search_history_by_saturation(min_score: float = 0.0, grade: str | None = None) -> List[Dict[str, Any]]:
    results = []
    for entry in get_history():
        expr = entry if isinstance(entry, str) else entry.get("expression", "")
        result = assess_saturation(expr)
        if result.error:
            continue
        if result.overall < min_score:
            continue
        if grade and result.grade != grade:
            continue
        results.append({
            "expression": expr,
            "description": _safe_humanize(expr),
            "overall": result.overall,
            "grade": result.grade,
            "source": "history",
        })
    return results


def search_favorites_by_saturation(min_score: float = 0.0, grade: str | None = None) -> List[Dict[str, Any]]:
    results = []
    for name, expr in list_favorites():
        result = assess_saturation(expr)
        if result.error:
            continue
        if result.overall < min_score:
            continue
        if grade and result.grade != grade:
            continue
        results.append({
            "name": name,
            "expression": expr,
            "description": _safe_humanize(expr),
            "overall": result.overall,
            "grade": result.grade,
            "source": "favorites",
        })
    return results
