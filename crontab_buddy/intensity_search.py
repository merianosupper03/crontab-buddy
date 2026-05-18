"""Search history and favorites by intensity grade or score threshold."""

from __future__ import annotations
from typing import Any
from crontab_buddy.intensity import assess_intensity
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid)"


def search_history_by_intensity(grade: str) -> list[dict[str, Any]]:
    """Return history entries whose intensity grade matches the given grade."""
    grade = grade.lower()
    results = []
    seen: set[str] = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        r = assess_intensity(expr)
        if r.error:
            continue
        if r.grade == grade:
            seen.add(expr)
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "grade": r.grade,
                "score": r.score,
                "runs_per_day": r.runs_per_day,
                "source": "history",
            })
    return results


def search_favorites_by_intensity(grade: str) -> list[dict[str, Any]]:
    """Return favorites whose intensity grade matches the given grade."""
    grade = grade.lower()
    results = []
    for name, expr in list_favorites():
        r = assess_intensity(expr)
        if r.error:
            continue
        if r.grade == grade:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "grade": r.grade,
                "score": r.score,
                "runs_per_day": r.runs_per_day,
                "source": "favorites",
            })
    return results


def search_above_score(threshold: float) -> list[dict[str, Any]]:
    """Return history entries with intensity score above the given threshold."""
    results = []
    seen: set[str] = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        r = assess_intensity(expr)
        if r.error:
            continue
        if r.score >= threshold:
            seen.add(expr)
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "grade": r.grade,
                "score": r.score,
                "runs_per_day": r.runs_per_day,
                "source": "history",
            })
    return sorted(results, key=lambda x: x["score"], reverse=True)
