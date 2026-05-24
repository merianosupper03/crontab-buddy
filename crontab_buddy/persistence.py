"""Persistence scoring: how reliably a cron expression maintains consistent scheduling."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds


PERSISTENCE_GRADES = [
    (0.90, "ironclad"),
    (0.75, "durable"),
    (0.55, "stable"),
    (0.35, "fragile"),
    (0.15, "erratic"),
    (0.0,  "volatile"),
]


def _grade(score: float) -> str:
    for threshold, label in PERSISTENCE_GRADES:
        if score >= threshold:
            return label
    return "volatile"


@dataclass
class PersistenceResult:
    expression: str
    score: float
    grade: str
    interval_seconds: Optional[int]
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"PersistenceResult({self.expression!r}, error={self.error!r})"
        return (
            f"PersistenceResult({self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r}, "
            f"interval={self.interval_seconds}s)"
        )


def assess_persistence(expression: str) -> PersistenceResult:
    """Score how persistent/reliable a cron schedule is.

    Higher scores mean more consistent, predictable scheduling.
    Very frequent schedules score lower because they are harder to sustain
    without resource contention.
    """
    try:
        CronExpression(expression)
    except CronParseError as exc:
        return PersistenceResult(
            expression=expression,
            score=0.0,
            grade="volatile",
            interval_seconds=None,
            error=str(exc),
        )

    interval = recurrence_interval_seconds(expression)

    if interval is None or interval <= 0:
        score = 0.0
    else:
        # Normalise: daily (86400s) = 1.0, every-minute (60s) approaches 0
        # Use a logarithmic scale capped at 1.0
        import math
        score = min(1.0, math.log(interval + 1) / math.log(86400 + 1))

    return PersistenceResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        interval_seconds=interval,
    )


def batch_persistence(expressions: list[str]) -> list[PersistenceResult]:
    return [assess_persistence(expr) for expr in expressions]
