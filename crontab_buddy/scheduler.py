"""Compute next N run times for a cron expression."""

from datetime import datetime, timedelta
from typing import List

from .parser import CronExpression


def _matches_field(value: int, field: str, min_val: int, max_val: int) -> bool:
    """Check if a value matches a cron field."""
    if field == "*":
        return True
    if "/" in field:
        base, step = field.split("/")
        step = int(step)
        start = min_val if base == "*" else int(base)
        return value >= start and (value - start) % step == 0
    if "," in field:
        return value in {int(p) for p in field.split(",")}
    if "-" in field:
        lo, hi = field.split("-")
        return int(lo) <= value <= int(hi)
    return value == int(field)


def next_runs(expr: CronExpression, count: int = 5, after: datetime = None) -> List[datetime]:
    """Return the next `count` datetimes matching the cron expression."""
    if after is None:
        after = datetime.now().replace(second=0, microsecond=0)

    results: List[datetime] = []
    current = after + timedelta(minutes=1)
    # Limit search to ~1 year of minutes to avoid infinite loops
    max_iterations = 525_600
    iterations = 0

    while len(results) < count and iterations < max_iterations:
        iterations += 1
        if (
            _matches_field(current.minute, expr.minute, 0, 59)
            and _matches_field(current.hour, expr.hour, 0, 23)
            and _matches_field(current.day, expr.day, 1, 31)
            and _matches_field(current.month, expr.month, 1, 12)
            and _matches_field(current.weekday() + 1, expr.weekday, 1, 7)
        ):
            results.append(current)
        current += timedelta(minutes=1)

    return results
