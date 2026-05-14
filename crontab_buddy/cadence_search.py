"""Search history and favorites by cadence classification."""

from typing import List, Dict, Any

from crontab_buddy.cadence import classify_cadence
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites


def _safe_humanize(expression: str) -> str:
    try:
        from crontab_buddy.humanizer import humanize
        from crontab_buddy.parser import CronExpression
        return humanize(CronExpression(expression))
    except Exception:
        return ""


def search_history_by_cadence(cadence: str) -> List[Dict[str, Any]]:
    """Return history entries whose cadence matches the given label."""
    cadence = cadence.lower().strip()
    results = []
    seen = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        try:
            result = classify_cadence(expr)
            if result.get("cadence", "").lower() == cadence:
                seen.add(expr)
                results.append({
                    "expression": expr,
                    "description": _safe_humanize(expr),
                    "cadence": result.get("cadence"),
                    "source": "history",
                })
        except Exception:
            pass
    return results


def search_favorites_by_cadence(cadence: str) -> List[Dict[str, Any]]:
    """Return favorites whose cadence matches the given label."""
    cadence = cadence.lower().strip()
    results = []
    for name, expr in list_favorites().items():
        try:
            result = classify_cadence(expr)
            if result.get("cadence", "").lower() == cadence:
                results.append({
                    "name": name,
                    "expression": expr,
                    "description": _safe_humanize(expr),
                    "cadence": result.get("cadence"),
                    "source": "favorites",
                })
        except Exception:
            pass
    return results


def search_all_by_cadence(cadence: str) -> List[Dict[str, Any]]:
    """Search both history and favorites by cadence."""
    return search_history_by_cadence(cadence) + search_favorites_by_cadence(cadence)
