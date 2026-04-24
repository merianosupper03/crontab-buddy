"""Search utilities for budgets."""

from __future__ import annotations

from typing import Any, Dict, List

from crontab_buddy.budget import list_budgets
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def search_budgets(
    query: str,
    path: str | None = None,
) -> List[Dict[str, Any]]:
    """Return budget entries whose expression or description contains *query*.

    Args:
        query: Case-insensitive substring to search for.
        path:  Optional path to the budgets JSON file.

    Returns:
        List of matching budget dicts, each with an extra ``description`` key.
    """
    kwargs: Dict[str, Any] = {}
    if path is not None:
        kwargs["path"] = path

    q = query.lower()
    results: List[Dict[str, Any]] = []

    for entry in list_budgets(**kwargs):
        desc = _safe_humanize(entry["expression"])
        if q in entry["expression"].lower() or q in desc.lower():
            results.append({**entry, "description": desc})

    return results
