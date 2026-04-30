"""Impact assessment for cron expressions — estimates how many times
an expression fires over a given period and rates the overall impact."""

from __future__ import annotations

from typing import Optional

from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds

_LEVELS = [
    (60 * 60 * 24 * 7, "low"),       # less than once a week
    (60 * 60 * 24, "moderate"),      # less than once a day
    (60 * 60, "elevated"),           # less than once an hour
    (0, "high"),                     # once an hour or more
]


class ImpactResult:
    def __init__(
        self,
        expression: str,
        runs_per_day: float,
        runs_per_week: float,
        runs_per_month: float,
        level: str,
        interval_seconds: Optional[int],
    ) -> None:
        self.expression = expression
        self.runs_per_day = runs_per_day
        self.runs_per_week = runs_per_week
        self.runs_per_month = runs_per_month
        self.level = level
        self.interval_seconds = interval_seconds

    def __str__(self) -> str:
        return (
            f"Expression : {self.expression}\n"
            f"Impact     : {self.level}\n"
            f"Runs/day   : {self.runs_per_day:.1f}\n"
            f"Runs/week  : {self.runs_per_week:.1f}\n"
            f"Runs/month : {self.runs_per_month:.1f}"
        )


def assess_impact(expression: str) -> ImpactResult:
    """Return an ImpactResult for the given cron expression string.

    Raises CronParseError if the expression is invalid.
    """
    expr = CronExpression(expression)  # may raise CronParseError
    interval = recurrence_interval_seconds(expr)

    if interval and interval > 0:
        seconds_per_day = 86_400
        runs_per_day = seconds_per_day / interval
    else:
        # Fallback: treat as once per day if interval is unknown
        runs_per_day = 1.0
        interval = None

    runs_per_week = runs_per_day * 7
    runs_per_month = runs_per_day * 30

    level = "low"
    for threshold, lbl in _LEVELS:
        if (interval or 0) <= threshold:
            level = lbl
            break
    # Re-derive level cleanly based on runs_per_day
    if runs_per_day >= 60:
        level = "high"
    elif runs_per_day >= 1:
        level = "elevated"
    elif runs_per_day >= 1 / 7:
        level = "moderate"
    else:
        level = "low"

    return ImpactResult(
        expression=expression,
        runs_per_day=round(runs_per_day, 4),
        runs_per_week=round(runs_per_week, 4),
        runs_per_month=round(runs_per_month, 4),
        level=level,
        interval_seconds=interval,
    )
