"""Search feedback entries by keyword or sentiment."""
from __future__ import annotations

from typing import Dict, List

from crontab_buddy.feedback import list_all_feedback
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return ""


def search_feedback(
    query: str,
    sentiment: str | None = None,
    path: str | None = None,
) -> List[Dict]:
    """
    Search feedback entries by query string and optional sentiment filter.

    Returns a list of dicts with keys: expression, description, sentiment, comment, timestamp.
    """
    kwargs = {"path": path} if path else {}
    all_fb = list_all_feedback(**kwargs)
    query_lower = query.lower()
    results: List[Dict] = []

    for expr, entries in all_fb.items():
        description = _safe_humanize(expr)
        for entry in entries:
            if sentiment and entry.get("sentiment") != sentiment:
                continue
            comment = entry.get("comment", "")
            if (
                query_lower in expr.lower()
                or query_lower in description.lower()
                or query_lower in comment.lower()
            ):
                results.append({
                    "expression": expr,
                    "description": description,
                    "sentiment": entry.get("sentiment", ""),
                    "comment": comment,
                    "timestamp": entry.get("timestamp", ""),
                })

    return results
