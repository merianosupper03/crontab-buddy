"""Search through history and favorites by expression or tag."""

from typing import List, Dict, Any
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.tags import get_tags
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except CronParseError:
        return "(invalid expression)"


def search_history(query: str) -> List[Dict[str, Any]]:
    """Return history entries whose expression contains the query string."""
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        if query.lower() in expr.lower():
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "source": "history",
                "timestamp": entry.get("timestamp"),
            })
    return results


def search_favorites(query: str) -> List[Dict[str, Any]]:
    """Return favorites whose name or expression contains the query string."""
    results = []
    for name, expr in list_favorites().items():
        if query.lower() in name.lower() or query.lower() in expr.lower():
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "source": "favorites",
            })
    return results


def search_by_tag(tag: str, path: str = None) -> List[Dict[str, Any]]:
    """Return expressions that have the given tag."""
    from crontab_buddy.tags import _load
    data = _load(path) if path else _load()
    results = []
    for expr, tags in data.items():
        if tag in tags:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "tags": tags,
                "source": "tags",
            })
    return results


def search_all(query: str) -> List[Dict[str, Any]]:
    """Search across history and favorites."""
    seen = set()
    results = []
    for item in search_history(query) + search_favorites(query):
        expr = item["expression"]
        if expr not in seen:
            seen.add(expr)
            results.append(item)
    return results
