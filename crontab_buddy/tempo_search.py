"""Search history and favorites by tempo level."""
from crontab_buddy.tempo import assess_tempo
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except (CronParseError, Exception):
        return "(invalid)"


def search_history_by_tempo(level: str) -> list:
    """Return history entries whose tempo matches the given level."""
    level = level.lower()
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        result = assess_tempo(expr)
        if result.level == level:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "level": result.level,
                "score": result.score,
                "source": "history",
            })
    return results


def search_favorites_by_tempo(level: str) -> list:
    """Return favorites whose tempo matches the given level."""
    level = level.lower()
    results = []
    for name, expr in list_favorites().items():
        result = assess_tempo(expr)
        if result.level == level:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "level": result.level,
                "score": result.score,
                "source": "favorites",
            })
    return results


def search_all_by_tempo(level: str) -> list:
    """Search both history and favorites by tempo level."""
    return search_history_by_tempo(level) + search_favorites_by_tempo(level)
