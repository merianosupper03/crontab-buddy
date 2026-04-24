"""Search utilities for cron expression variables."""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict

from crontab_buddy.variable import list_variables
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return ""


def search_variables(
    query: str,
    path: Path | None = None,
) -> List[Dict[str, str]]:
    """Search variables by name or expression substring (case-insensitive).

    Returns a list of matching {name, expression, description} dicts.
    """
    kwargs = {"path": path} if path is not None else {}
    variables = list_variables(**kwargs)
    q = query.lower()
    results = []
    for v in variables:
        description = _safe_humanize(v["expression"])
        if (
            q in v["name"].lower()
            or q in v["expression"].lower()
            or q in description.lower()
        ):
            results.append(
                {
                    "name": v["name"],
                    "expression": v["expression"],
                    "description": description,
                }
            )
    return results
