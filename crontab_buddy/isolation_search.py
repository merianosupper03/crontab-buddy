"""Search history and favorites by isolation grade/score."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.isolation import assess_isolation

try:
    from crontab_buddy.humanizer import humanize
    from crontab_buddy.parser import CronExpression, CronParseError

    def _safe_humanize(expr: str) -> str:
        try:
            return humanize(CronExpression(expr))
        except CronParseError:
            return "(invalid)"
except Exception:  # pragma: no cover
    def _safe_humanize(expr: str) -> str:  # type: ignore
        return ""


def search_history_by_isolation(
    min_score: float = 0.0,
    grade: Optional[str] = None,
    peers: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Return history entries whose isolation score meets the criteria."""
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        r = assess_isolation(expr, peers or [])
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


def search_favorites_by_isolation(
    min_score: float = 0.0,
    grade: Optional[str] = None,
    peers: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Return favorites whose isolation score meets the criteria."""
    results = []
    for name, expr in list_favorites().items():
        r = assess_isolation(expr, peers or [])
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
