"""Search history and favorites by density score."""

from __future__ import annotations

from typing import Any, Dict, List

from crontab_buddy.density_score import compute_density_score
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites

try:
    from crontab_buddy.humanizer import humanize
    from crontab_buddy.parser import CronExpression, CronParseError

    def _safe_humanize(expression: str) -> str:
        try:
            return humanize(CronExpression(expression))
        except (CronParseError, ValueError):
            return expression

except Exception:
    def _safe_humanize(expression: str) -> str:  # type: ignore[misc]
        return expression


def search_history_by_density_score(
    min_score: float = 0.0,
    max_score: float = 1.0,
) -> List[Dict[str, Any]]:
    results = []
    seen = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = compute_density_score(expr)
        if r.error:
            continue
        if min_score <= r.score <= max_score:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": r.score,
                "grade": r.grade,
                "fires_per_day": r.fires_per_day,
                "source": "history",
            })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def search_favorites_by_density_score(
    min_score: float = 0.0,
    max_score: float = 1.0,
) -> List[Dict[str, Any]]:
    results = []
    for name, expr in list_favorites().items():
        r = compute_density_score(expr)
        if r.error:
            continue
        if min_score <= r.score <= max_score:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": r.score,
                "grade": r.grade,
                "fires_per_day": r.fires_per_day,
                "source": "favorites",
            })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
