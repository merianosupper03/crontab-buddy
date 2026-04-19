"""Search named schedules by name or expression substring."""

from pathlib import Path
from crontab_buddy.schedule_name import list_schedules
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return ""


def search_schedules(query: str, path: Path = None) -> list:
    """Search named schedules by name, expression, description, or human-readable text."""
    kwargs = {"path": path} if path else {}
    schedules = list_schedules(**kwargs)
    query_lower = query.lower()
    results = []
    for name, entry in schedules.items():
        expr = entry.get("expression", "")
        desc = entry.get("description", "")
        readable = _safe_humanize(expr)
        if (
            query_lower in name
            or query_lower in expr.lower()
            or query_lower in desc.lower()
            or query_lower in readable.lower()
        ):
            results.append({
                "name": name,
                "expression": expr,
                "description": desc,
                "readable": readable,
            })
    return results
