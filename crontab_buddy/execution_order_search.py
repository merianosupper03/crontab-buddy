"""Search across execution order queues."""

from __future__ import annotations

from typing import List, Dict, Any

from crontab_buddy.execution_order import _load, get_queue, list_queues
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return ""


def search_queues(query: str, path: str | None = None) -> List[Dict[str, Any]]:
    """Search all queues for expressions matching query string.

    Returns a list of dicts with keys: queue, position, expression, description.
    """
    from crontab_buddy.execution_order import _DEFAULT_PATH

    effective_path = path or _DEFAULT_PATH
    results: List[Dict[str, Any]] = []
    q_lower = query.lower()

    for queue_name in list_queues(path=effective_path):
        for pos, expr in enumerate(get_queue(queue_name, path=effective_path), 1):
            desc = _safe_humanize(expr)
            if q_lower in expr.lower() or q_lower in desc.lower():
                results.append(
                    {
                        "queue": queue_name,
                        "position": pos,
                        "expression": expr,
                        "description": desc,
                    }
                )
    return results
