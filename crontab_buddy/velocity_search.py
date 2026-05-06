"""Search history / favorites by velocity level."""

from __future__ import annotations

from typing import List, Dict

from crontab_buddy.velocity import compute_velocity, _WINDOWS
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites


def _safe_humanize(expression: str) -> str:
    try:
        from crontab_buddy.humanizer import humanize
        from crontab_buddy.parser import CronExpression
        return humanize(CronExpression(expression))
    except Exception:
        return expression


def search_history_by_velocity(level: str, window: str = "24h") -> List[Dict]:
    """Return unique history expressions whose velocity matches *level*."""
    seen = set()
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        try:
            r = compute_velocity(expr, window)
        except ValueError:
            continue
        if r.level == level:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "level": r.level,
                "rate_per_hour": r.rate_per_hour,
                "count": r.count,
                "source": "history",
            })
    return results


def search_favorites_by_velocity(level: str, window: str = "24h") -> List[Dict]:
    """Return favorites whose velocity matches *level*."""
    results = []
    for name, expr in list_favorites().items():
        try:
            r = compute_velocity(expr, window)
        except ValueError:
            continue
        if r.level == level:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "level": r.level,
                "rate_per_hour": r.rate_per_hour,
                "count": r.count,
                "source": "favorites",
            })
    return results
