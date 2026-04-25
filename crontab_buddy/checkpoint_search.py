"""Standalone search utility for checkpoints, usable from search_all."""

from __future__ import annotations

from typing import List, Dict

from crontab_buddy.checkpoint import list_checkpoints
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid)"


def search_checkpoints(query: str, path: str | None = None) -> List[Dict]:
    """Search checkpoints and return result dicts with source label."""
    kwargs = {"path": path} if path else {}
    q = query.lower()
    results = []
    for cp in list_checkpoints(**kwargs):
        if (
            q in cp["name"]
            or q in cp["expression"].lower()
            or q in cp.get("note", "").lower()
            or q in _safe_humanize(cp["expression"]).lower()
        ):
            results.append({
                "source": "checkpoint",
                "name": cp["name"],
                "expression": cp["expression"],
                "description": _safe_humanize(cp["expression"]),
                "note": cp.get("note", ""),
            })
    return results
