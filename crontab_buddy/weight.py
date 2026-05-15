"""Weight scoring for cron expressions.

A 'weight' reflects how computationally heavy a schedule is likely to be,
based on firing frequency and field complexity.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds

_GRADES = [
    (0.2, "featherlight"),
    (0.4, "light"),
    (0.6, "moderate"),
    (0.8, "heavy"),
    (1.01, "crushing"),
]


def _grade(score: float) -> str:
    for threshold, label in _GRADES:
        if score < threshold:
            return label
    return "crushing"


@dataclass
class WeightResult:
    expression: str
    score: float
    grade: str
    runs_per_day: float
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"WeightResult({self.expression!r}, error={self.error!r})"
        return (
            f"WeightResult({self.expression!r}, score={self.score:.3f}, "
            f"grade={self.grade!r}, runs_per_day={self.runs_per_day:.1f})"
        )


def assess_weight(expression: str) -> WeightResult:
    """Assess the scheduling weight of a cron expression."""
    try:
        CronExpression(expression)
    except CronParseError as exc:
        return WeightResult(
            expression=expression,
            score=0.0,
            grade="featherlight",
            runs_per_day=0.0,
            error=str(exc),
        )

    interval = recurrence_interval_seconds(expression)
    if interval <= 0:
        runs_per_day = 0.0
    else:
        runs_per_day = 86400.0 / interval

    # Normalise: 1440 runs/day (every minute) -> score ~1.0
    raw = runs_per_day / 1440.0
    score = min(raw, 1.0)

    return WeightResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        runs_per_day=round(runs_per_day, 2),
    )


def batch_weight(expressions: list[str]) -> list[WeightResult]:
    """Assess weight for a list of expressions."""
    return [assess_weight(e) for e in expressions]
