"""Inertia: measures how resistant a cron expression is to change based on its firing frequency.

High-frequency expressions have low inertia (easy to swap out).
Low-frequency expressions have high inertia (harder to replace without impact).
"""

from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.recurrence import recurrence_interval_seconds


def _grade(score: float) -> str:
    if score >= 0.85:
        return "immovable"
    if score >= 0.65:
        return "resistant"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "flexible"
    return "fluid"


@dataclass
class InertiaResult:
    expression: str
    score: float
    grade: str
    interval_seconds: Optional[int]
    description: str
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"InertiaResult(expression={self.expression!r}, error={self.error!r})"
        return (
            f"InertiaResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r})"
        )


def assess_inertia(expression: str) -> InertiaResult:
    """Assess the inertia of a cron expression.

    Score is 0.0 (fluid/high-frequency) to 1.0 (immovable/low-frequency).
    """
    try:
        interval = recurrence_interval_seconds(expression)
    except Exception as exc:
        return InertiaResult(
            expression=expression,
            score=0.0,
            grade="fluid",
            interval_seconds=None,
            description="",
            error=str(exc),
        )

    # Map interval to a 0-1 score: longer interval => higher inertia
    # Anchors: 60s (every minute) => 0.0, 604800s (weekly) => 1.0
    min_interval = 60
    max_interval = 604800
    clamped = max(min_interval, min(interval, max_interval))
    # Log scale for smoother gradient
    import math
    log_min = math.log(min_interval)
    log_max = math.log(max_interval)
    log_val = math.log(clamped)
    score = (log_val - log_min) / (log_max - log_min)

    grade = _grade(score)
    hours = interval / 3600
    description = f"Fires every ~{hours:.1f}h; inertia grade: {grade}"

    return InertiaResult(
        expression=expression,
        score=round(score, 4),
        grade=grade,
        interval_seconds=interval,
        description=description,
    )


def batch_inertia(expressions: list) -> list:
    """Assess inertia for a list of expressions."""
    return [assess_inertia(expr) for expr in expressions]
