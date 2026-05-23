"""Density score: measures how densely packed a cron expression's firings are
within a given time window, returning a normalized 0-1 score."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from crontab_buddy.parser import CronExpression, CronParseError

_GRADES = [
    (0.9, "packed"),
    (0.7, "dense"),
    (0.5, "moderate"),
    (0.3, "sparse"),
    (0.0, "minimal"),
]

_MINUTES_PER_DAY = 1440


def _grade(score: float) -> str:
    for threshold, label in _GRADES:
        if score >= threshold:
            return label
    return "minimal"


@dataclass
class DensityScoreResult:
    expression: str
    score: float
    grade: str
    fires_per_day: int
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"{self.expression} | error: {self.error}"
        return (
            f"{self.expression} | score={self.score:.3f} | "
            f"grade={self.grade} | fires/day={self.fires_per_day}"
        )


def _safe_parse(expression: str) -> Optional[CronExpression]:
    try:
        return CronExpression(expression)
    except (CronParseError, ValueError):
        return None


def _count_firing_minutes(expr: CronExpression) -> int:
    """Approximate daily firing count by iterating all minute/hour combos."""
    from crontab_buddy.scheduler import _matches_field

    count = 0
    for hour in range(24):
        if not _matches_field(expr.hour, hour, 0, 23):
            continue
        for minute in range(60):
            if _matches_field(expr.minute, minute, 0, 59):
                count += 1
    return count


def compute_density_score(expression: str) -> DensityScoreResult:
    expr = _safe_parse(expression)
    if expr is None:
        return DensityScoreResult(
            expression=expression,
            score=0.0,
            grade="minimal",
            fires_per_day=0,
            error="invalid expression",
        )
    fires = _count_firing_minutes(expr)
    score = round(fires / _MINUTES_PER_DAY, 4)
    score = min(1.0, max(0.0, score))
    return DensityScoreResult(
        expression=expression,
        score=score,
        grade=_grade(score),
        fires_per_day=fires,
    )
