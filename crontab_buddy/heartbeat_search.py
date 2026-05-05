"""Search utilities for heartbeat records."""
from __future__ import annotations

from typing import List, Dict

from crontab_buddy.heartbeat import list_heartbeats
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return ""


def search_heartbeats(query: str, status_filter: str = None) -> List[Dict]:
    """Search heartbeat records by expression or description.

    Optionally filter by status ('ok', 'warn', 'fail').
    Returns a list of dicts with expression, description, and latest record.
    """
    query_lower = query.lower()
    data = list_heartbeats()
    results = []

    for expr, records in data.items():
        desc = _safe_humanize(expr)
        if query_lower not in expr.lower() and query_lower not in desc.lower():
            continue

        if status_filter:
            matching = [r for r in records if r["status"] == status_filter]
        else:
            matching = records

        if not matching:
            continue

        latest = max(matching, key=lambda r: r["timestamp"])
        results.append({
            "expression": expr,
            "description": desc,
            "latest": latest,
            "count": len(matching),
        })

    return results
