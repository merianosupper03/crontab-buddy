"""Search utilities for execution traces."""

from __future__ import annotations

from typing import List, Dict

from crontab_buddy import tracing
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid)"


def search_traces(
    keyword: str,
    status: str | None = None,
    path: str = tracing._DEFAULT_PATH,
) -> List[Dict]:
    """Search traces by keyword (matches expression or label) and optional status.

    Returns a flat list of matching span dicts, each augmented with a
    ``description`` key from the humanizer.
    """
    keyword_lower = keyword.lower()
    results: List[Dict] = []

    for expr in tracing.list_traced_expressions(path=path):
        if keyword_lower not in expr.lower():
            # also check humanized description
            desc = _safe_humanize(expr)
            if keyword_lower not in desc.lower():
                # still check individual span labels below
                pass
        description = _safe_humanize(expr)
        for span in tracing.get_traces(expr, path=path):
            label = (span.get("label") or "").lower()
            expr_match = keyword_lower in expr.lower()
            desc_match = keyword_lower in description.lower()
            label_match = keyword_lower in label
            if not (expr_match or desc_match or label_match):
                continue
            if status and span["status"] != status:
                continue
            results.append({**span, "description": description})

    return results
