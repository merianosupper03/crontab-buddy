"""Search history and favorites by polarity."""

from crontab_buddy.polarity import assess_polarity
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites


def _safe_humanize(expression: str) -> str:
    try:
        from crontab_buddy.humanizer import humanize
        from crontab_buddy.parser import CronExpression
        return humanize(CronExpression(expression))
    except Exception:
        return expression


def search_history_by_polarity(polarity: str) -> list:
    """Return history entries whose polarity matches the given label."""
    results = []
    for entry in get_history():
        expr = entry if isinstance(entry, str) else entry.get("expression", "")
        r = assess_polarity(expr)
        if r.polarity == polarity:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "polarity": r.polarity,
                "score": r.score,
                "source": "history",
            })
    return results


def search_favorites_by_polarity(polarity: str) -> list:
    """Return favorites whose polarity matches the given label."""
    results = []
    for name, expr in list_favorites().items():
        r = assess_polarity(expr)
        if r.polarity == polarity:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "polarity": r.polarity,
                "score": r.score,
                "source": "favorites",
            })
    return results


def search_all_by_polarity(polarity: str) -> list:
    """Return all entries (history + favorites) matching the given polarity."""
    return search_history_by_polarity(polarity) + search_favorites_by_polarity(polarity)
