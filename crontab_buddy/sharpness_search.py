"""Search history and favorites by sharpness grade or score threshold."""

from crontab_buddy.sharpness import assess_sharpness
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except (CronParseError, Exception):
        return "(invalid)"


def search_history_by_sharpness(min_score: float = 0.0, grade: str = None) -> list:
    """Return history entries whose sharpness meets the criteria."""
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        r = assess_sharpness(expr)
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
    return results


def search_favorites_by_sharpness(min_score: float = 0.0, grade: str = None) -> list:
    """Return favorites whose sharpness meets the criteria."""
    results = []
    for name, expr in list_favorites():
        r = assess_sharpness(expr)
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
    return results


def search_above_score(threshold: float) -> list:
    """Return all history + favorites entries above a sharpness score."""
    hist = search_history_by_sharpness(min_score=threshold)
    favs = search_favorites_by_sharpness(min_score=threshold)
    seen = set()
    combined = []
    for item in hist + favs:
        key = item["expression"]
        if key not in seen:
            seen.add(key)
            combined.append(item)
    return sorted(combined, key=lambda x: x["score"], reverse=True)
