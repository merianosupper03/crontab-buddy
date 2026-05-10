"""Latency estimation for cron expressions.

Estimates the expected time between consecutive firings and grades
the expression based on how "responsive" it is.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.recurrence import recurrence_interval_seconds
from crontab_buddy.parser import CronExpression, CronParseError


_GRADES = [
    (60, "instant"),
    (300, "rapid"),
    (1800, "frequent"),
    (3600, "regular"),
    (86400, "infrequent"),
    (float("inf"), "rare"),
]


def _grade(interval_seconds: float) -> str:
    for threshold, label in _GRADES:
        if interval_seconds <= threshold:
            return label
    return "rare"


@dataclass
class LatencyResult:
    expression: str
    interval_seconds: Optional[float]
    grade: str
    error: Optional[str] = field(default=None)

    def __str__(self) -> str:
        if self.error:
            return f"LatencyResult({self.expression!r}, error={self.error!r})"
        minutes = (self.interval_seconds or 0) / 60
        return (
            f"LatencyResult({self.expression!r}, "
            f"interval={minutes:.1f}m, grade={self.grade!r})"
        )


def assess_latency(expression: str) -> LatencyResult:
    """Assess the latency (inter-firing interval) of a cron expression."""
    try:
        CronExpression(expression)
    except CronParseError as exc:
        return LatencyResult(
            expression=expression,
            interval_seconds=None,
            grade="unknown",
            error=str(exc),
        )

    interval = recurrence_interval_seconds(expression)
    if interval is None:
        return LatencyResult(
            expression=expression,
            interval_seconds=None,
            grade="unknown",
            error="could not determine interval",
        )

    return LatencyResult(
        expression=expression,
        interval_seconds=float(interval),
        grade=_grade(float(interval)),
    )


def batch_latency(expressions: list[str]) -> list[LatencyResult]:
    """Assess latency for multiple expressions."""
    return [assess_latency(expr) for expr in expressions]
