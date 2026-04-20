"""Search throttle settings by expression or unit."""

from typing import List, Dict, Any
from crontab_buddy.throttle import list_throttles
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError
from pathlib import Path


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def search_throttles(
    query: str,
    path: Path = None,
) -> List[Dict[str, Any]]:
    """Search throttles by expression string, description, or unit.

    Returns a list of dicts with keys: expression, description, interval, unit.
    """
    kwargs = {"path": path} if path else {}
    all_throttles = list_throttles(**kwargs)
    query_lower = query.lower()
    results = []
    for expr, cfg in all_throttles.items():
        desc = _safe_humanize(expr)
        if (
            query_lower in expr.lower()
            or query_lower in desc.lower()
            or query_lower in cfg["unit"].lower()
        ):
            results.append(
                {
                    "expression": expr,
                    "description": desc,
                    "interval": cfg["interval"],
                    "unit": cfg["unit"],
                }
            )
    return results
