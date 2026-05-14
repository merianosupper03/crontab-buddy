"""Search history and favorites by fidelity grade or score threshold."""

from typing import List, Dict, Any

from crontab_buddy.fidelity import assess_fidelity
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except (CronParseError, Exception):
        return ""


def search_history_by_fidelity(min_score: float = 0.0) -> List[Dict[str, Any]]:
    """Return history entries whose fidelity score meets the threshold."""
    results = []
    seen = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        result = assess_fidelity(expr)
        if result.error:
            continue
        if result.score >= min_score:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": result.score,
                "grade": result.grade,
                "source": "history",
            })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def search_favorites_by_fidelity(min_score: float = 0.0) -> List[Dict[str, Any]]:
    """Return favorites whose fidelity score meets the threshold."""
    results = []
    for name, expr in list_favorites():
        result = assess_fidelity(expr)
        if result.error:
            continue
        if result.score >= min_score:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": result.score,
                "grade": result.grade,
                "source": "favorites",
            })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def search_above_score(min_score: float = 0.5) -> List[Dict[str, Any]]:
    """Search both history and favorites for expressions above a fidelity score."""
    combined = search_history_by_fidelity(min_score) + search_favorites_by_fidelity(min_score)
    seen = set()
    unique = []
    for item in combined:
        if item["expression"] not in seen:
            seen.add(item["expression"])
            unique.append(item)
    unique.sort(key=lambda r: r["score"], reverse=True)
    return unique
