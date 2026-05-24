"""Search history and favorites for expressions with cadence gaps."""

from typing import List, Dict, Any

from crontab_buddy.cadence_gap import find_cadence_gaps
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except (CronParseError, Exception):
        return ""


def search_history_with_gaps(min_gap_hours: int = 1) -> List[Dict[str, Any]]:
    """Return history entries whose expressions have at least min_gap_hours uncovered."""
    results = []
    seen = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        gaps = find_cadence_gaps([expr])
        if len(gaps) >= min_gap_hours:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "gap_hours": gaps,
                "gap_count": len(gaps),
                "source": "history",
            })
    return results


def search_favorites_with_gaps(min_gap_hours: int = 1) -> List[Dict[str, Any]]:
    """Return favorites whose expressions have at least min_gap_hours uncovered."""
    results = []
    for name, expr in list_favorites().items():
        gaps = find_cadence_gaps([expr])
        if len(gaps) >= min_gap_hours:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "gap_hours": gaps,
                "gap_count": len(gaps),
                "source": "favorites",
            })
    return results


def search_all_with_gaps(min_gap_hours: int = 1) -> List[Dict[str, Any]]:
    """Combine history and favorites gap search, deduplicating by expression."""
    seen = set()
    combined = []
    for item in search_history_with_gaps(min_gap_hours) + search_favorites_with_gaps(min_gap_hours):
        expr = item["expression"]
        if expr not in seen:
            seen.add(expr)
            combined.append(item)
    return combined
