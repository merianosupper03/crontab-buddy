"""Search history/favorites by elasticity grade or score threshold."""

from __future__ import annotations
from crontab_buddy.elasticity import assess_elasticity
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid)"


def search_history_by_elasticity(min_score: float = 0.0, grade: str | None = None) -> list[dict]:
    results = []
    seen = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = assess_elasticity(expr)
        if r.error:
            continue
        if r.score < min_score:
            continue
        if grade and r.grade != grade:
            continue
        results.append({
            "expression": expr,
            "score": r.score,
            "grade": r.grade,
            "description": _safe_humanize(expr),
            "source": "history",
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def search_favorites_by_elasticity(min_score: float = 0.0, grade: str | None = None) -> list[dict]:
    results = []
    for name, expr in list_favorites().items():
        r = assess_elasticity(expr)
        if r.error:
            continue
        if r.score < min_score:
            continue
        if grade and r.grade != grade:
            continue
        results.append({
            "name": name,
            "expression": expr,
            "score": r.score,
            "grade": r.grade,
            "description": _safe_humanize(expr),
            "source": "favorites",
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def search_above_score(threshold: float) -> list[dict]:
    hist = search_history_by_elasticity(min_score=threshold)
    favs = search_favorites_by_elasticity(min_score=threshold)
    seen = set()
    combined = []
    for item in hist + favs:
        key = item["expression"]
        if key not in seen:
            seen.add(key)
            combined.append(item)
    combined.sort(key=lambda x: x["score"], reverse=True)
    return combined
