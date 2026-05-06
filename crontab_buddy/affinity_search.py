"""Search utilities that use affinity scoring against stored favorites/history."""

from typing import List, Dict, Any

from crontab_buddy.affinity import assess_affinity
from crontab_buddy.favorites import list_favorites
from crontab_buddy.history import get_history


def _safe_humanize(expr: str) -> str:
    try:
        from crontab_buddy.humanizer import humanize
        from crontab_buddy.parser import CronExpression
        return humanize(CronExpression(expr))
    except Exception:
        return expr


def find_complementary_favorites(expr: str, min_score: float = 0.5) -> List[Dict[str, Any]]:
    """Return favorites whose affinity with *expr* meets *min_score*."""
    results = []
    for name, stored_expr in list_favorites():
        if stored_expr == expr:
            continue
        result = assess_affinity(expr, stored_expr)
        if result.score >= min_score:
            results.append({
                "name": name,
                "expression": stored_expr,
                "description": _safe_humanize(stored_expr),
                "score": result.score,
                "grade": result.grade,
            })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def find_complementary_history(expr: str, min_score: float = 0.5) -> List[Dict[str, Any]]:
    """Return history entries whose affinity with *expr* meets *min_score*."""
    seen: set = set()
    results = []
    for entry in get_history():
        stored_expr = entry.get("expression", "")
        if not stored_expr or stored_expr == expr or stored_expr in seen:
            continue
        seen.add(stored_expr)
        result = assess_affinity(expr, stored_expr)
        if result.score >= min_score:
            results.append({
                "expression": stored_expr,
                "description": _safe_humanize(stored_expr),
                "score": result.score,
                "grade": result.grade,
            })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results
