"""Search history and favorites by volatility level."""

from crontab_buddy.volatility import assess_volatility
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites


def _safe_humanize(expression: str) -> str:
    try:
        from crontab_buddy.humanizer import humanize
        from crontab_buddy.parser import CronExpression
        return humanize(CronExpression(expression))
    except Exception:
        return expression


def search_history_by_volatility(level: str) -> list:
    """Return history entries matching the given volatility level."""
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        r = assess_volatility(expr)
        if r.valid and r.level == level:
            results.append({
                "expression": expr,
                "level": r.level,
                "score": r.score,
                "description": _safe_humanize(expr),
                "source": "history",
            })
    return results


def search_favorites_by_volatility(level: str) -> list:
    """Return favorites matching the given volatility level."""
    results = []
    for name, expr in list_favorites().items():
        r = assess_volatility(expr)
        if r.valid and r.level == level:
            results.append({
                "name": name,
                "expression": expr,
                "level": r.level,
                "score": r.score,
                "description": _safe_humanize(expr),
                "source": "favorites",
            })
    return results


def search_all_by_volatility(level: str) -> list:
    """Search both history and favorites by volatility level."""
    return search_history_by_volatility(level) + search_favorites_by_volatility(level)
