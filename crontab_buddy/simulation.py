"""Simulation module for crontab-buddy.

Allows dry-running a cron expression over a time range to see
how many times it would fire and when, without actually scheduling anything.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from .parser import CronExpression, CronParseError
from .scheduler import _matches_field
from .humanizer import humanize


# ---------------------------------------------------------------------------
# Core simulation logic
# ---------------------------------------------------------------------------

def simulate(
    expression: str,
    start: datetime,
    end: datetime,
    max_hits: int = 500,
) -> List[datetime]:
    """Return every minute within [start, end) that matches *expression*.

    Args:
        expression: A five-field cron expression string.
        start:      Inclusive start of the simulation window.
        end:        Exclusive end of the simulation window.
        max_hits:   Safety cap – stop collecting after this many matches.

    Returns:
        Sorted list of matching datetimes (second/microsecond zeroed out).

    Raises:
        CronParseError: If *expression* cannot be parsed.
        ValueError:     If *start* is not before *end*.
    """
    if start >= end:
        raise ValueError("start must be before end")

    expr = CronExpression(expression)  # raises CronParseError on bad input

    hits: List[datetime] = []
    cursor = start.replace(second=0, microsecond=0)

    while cursor < end:
        if (
            _matches_field(expr.minute, cursor.minute)
            and _matches_field(expr.hour, cursor.hour)
            and _matches_field(expr.dom, cursor.day)
            and _matches_field(expr.month, cursor.month)
            and _matches_field(expr.dow, cursor.weekday())
        ):
            hits.append(cursor)
            if len(hits) >= max_hits:
                break
        cursor += timedelta(minutes=1)

    return hits


# ---------------------------------------------------------------------------
# Summary helpers
# ---------------------------------------------------------------------------

def simulation_summary(
    expression: str,
    start: datetime,
    end: datetime,
    max_hits: int = 500,
) -> dict:
    """Return a structured summary dict for a simulation run.

    Keys:
        expression  – original cron string
        description – human-readable description
        start       – ISO-formatted start timestamp
        end         – ISO-formatted end timestamp
        hit_count   – number of matches found
        capped      – True if max_hits was reached
        hits        – list of ISO-formatted match timestamps
    """
    try:
        hits = simulate(expression, start, end, max_hits=max_hits)
        try:
            description = humanize(expression)
        except Exception:
            description = ""
        return {
            "expression": expression,
            "description": description,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "hit_count": len(hits),
            "capped": len(hits) >= max_hits,
            "hits": [h.isoformat() for h in hits],
        }
    except CronParseError as exc:
        return {
            "expression": expression,
            "description": "",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "hit_count": 0,
            "capped": False,
            "hits": [],
            "error": str(exc),
        }


def format_simulation(summary: dict, max_display: int = 10) -> str:
    """Render a simulation summary as a human-readable string."""
    lines = [
        f"Expression : {summary['expression']}",
    ]
    if summary.get("description"):
        lines.append(f"Description: {summary['description']}")
    if summary.get("error"):
        lines.append(f"Error      : {summary['error']}")
        return "\n".join(lines)

    lines += [
        f"Window     : {summary['start']}  →  {summary['end']}",
        f"Matches    : {summary['hit_count']}"
        + ("  (capped)" if summary["capped"] else ""),
    ]
    if summary["hits"]:
        lines.append("First hits :")
        for ts in summary["hits"][:max_display]:
            lines.append(f"  {ts}")
        if summary["hit_count"] > max_display:
            lines.append(f"  … and {summary['hit_count'] - max_display} more")
    else:
        lines.append("No matches in the given window.")
    return "\n".join(lines)
