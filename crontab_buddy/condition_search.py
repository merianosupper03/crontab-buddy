"""Search across conditions attached to cron expressions."""

from typing import List, Dict, Any

from crontab_buddy.condition import get_conditions, _load
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    """Return a human-readable description or fallback string."""
    try:
        expr = CronExpression(expression)
        return humanize(expr)
    except (CronParseError, ValueError):
        return "(invalid expression)"


def search_conditions(
    query: str,
    path: str = None,
) -> List[Dict[str, Any]]:
    """Search conditions by expression, type, value, or description.

    Args:
        query: Case-insensitive search term.
        path: Optional custom path to the conditions JSON file.

    Returns:
        A list of result dicts with keys:
            - expression: the cron expression string
            - description: human-readable form of the expression
            - conditions: list of matching condition dicts
    """
    q = query.lower().strip()
    data = _load(path) if path else _load()
    results: List[Dict[str, Any]] = []

    for expression, conditions in data.items():
        matched: List[Dict[str, Any]] = []

        for cond in conditions:
            # Match against expression string itself
            if q in expression.lower():
                matched = conditions
                break

            # Match against condition type
            cond_type = cond.get("type", "").lower()
            if q in cond_type:
                matched.append(cond)
                continue

            # Match against condition value
            cond_value = str(cond.get("value", "")).lower()
            if q in cond_value:
                matched.append(cond)
                continue

            # Match against optional description field
            cond_desc = cond.get("description", "").lower()
            if q in cond_desc:
                matched.append(cond)
                continue

        if matched:
            results.append(
                {
                    "expression": expression,
                    "description": _safe_humanize(expression),
                    "conditions": matched,
                }
            )

    return results
