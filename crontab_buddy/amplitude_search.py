"""Search history and favorites by amplitude grade or score threshold."""

from __future__ import annotations
from crontab_buddy.amplitude import assess_amplitude
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except (CronParseError, Exception):
        return "(invalid)"


def search_history_by_amplitude(grade: str) -> list[dict]:
    """Return history entries whose amplitude grade matches."""
    results = []
    seen: set[str] = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = assess_amplitude(expr)
        if r.grade == grade and not r.error:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": r.score,
                "grade": r.grade,
                "source": "history",
            })
    return sorted(results, key=lambda x: x["score"], reverse=True)


def search_favorites_by_amplitude(grade: str) -> list[dict]:
    """Return favorites whose amplitude grade matches."""
    results = []
    for name, expr in list_favorites():
        r = assess_amplitude(expr)
        if r.grade == grade and not r.error:
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
    """Return history entries with amplitude score above threshold."""
    results = []
    seen: set[str] = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = assess_amplitude(expr)
        if not r.error and r.score >= threshold:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": r.score,
                "grade": r.grade,
                "source": "history",
            })
    return sorted(results, key=lambda x: x["score"], reverse=True)
