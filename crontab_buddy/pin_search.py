"""Search through pinned expressions."""
from typing import List, Dict
from pathlib import Path
from crontab_buddy.pin import get_pins
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except CronParseError:
        return ""


def search_pins(query: str, path: Path = None) -> List[Dict]:
    """Search pinned expressions by expression string or description."""
    kwargs = {"path": path} if path else {}
    pins = get_pins(**kwargs)
    query_lower = query.lower()
    results = []
    for expr in pins:
        description = _safe_humanize(expr)
        if query_lower in expr.lower() or query_lower in description.lower():
            results.append({
                "expression": expr,
                "description": description,
                "source": "pins",
            })
    return results
