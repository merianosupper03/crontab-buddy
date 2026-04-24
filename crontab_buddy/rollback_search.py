"""Search across rollback stacks by expression or description fragment."""

from __future__ import annotations

from typing import List, Dict

from crontab_buddy.rollback import _load, _DEFAULT_PATH
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return ""


def search_rollbacks(
    query: str,
    path: str = _DEFAULT_PATH,
) -> List[Dict]:
    """Search all rollback stacks for entries matching the query string.

    Returns a list of dicts with keys: slot, expression, description, timestamp.
    """
    query_lower = query.lower()
    results: List[Dict] = []
    data = _load(path)

    for slot, stack in data.items():
        for entry in stack:
            expr = entry.get("expression", "")
            desc = _safe_humanize(expr)
            if query_lower in expr.lower() or query_lower in desc.lower():
                results.append(
                    {
                        "slot": slot,
                        "expression": expr,
                        "description": desc,
                        "timestamp": entry.get("timestamp", ""),
                    }
                )

    return results
