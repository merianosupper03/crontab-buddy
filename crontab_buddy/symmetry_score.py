"""Symmetry score: measures how evenly distributed firing minutes are across the hour."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.9:
        return "balanced"
    if score >= 0.7:
        return "near-balanced"
    if score >= 0.5:
        return "uneven"
    if score >= 0.25:
        return "skewed"
    return "asymmetric"


def _firing_minutes(expr: CronExpression) -> List[int]:
    minute_field = expr.fields[0]
    if minute_field == "*":
        return list(range(60))
    if "/" in minute_field:
        parts = minute_field.split("/")
        step = int(parts[1])
        start = 0 if parts[0] == "*" else int(parts[0])
        return list(range(start, 60, step))
    if "," in minute_field:
        return [int(x) for x in minute_field.split(",")]
    if "-" in minute_field:
        lo, hi = minute_field.split("-")
        return list(range(int(lo), int(hi) + 1))
    return [int(minute_field)]


@dataclass
class SymmetryScoreResult:
    expression: str
    score: float
    grade: str
    firing_count: int
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"SymmetryScore({self.expression!r}): error={self.error}"
        return (
            f"SymmetryScore({self.expression!r}): "
            f"score={self.score:.3f} grade={self.grade} "
            f"firing_count={self.firing_count}"
        )


def compute_symmetry_score(expression: str) -> SymmetryScoreResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return SymmetryScoreResult(
            expression=expression, score=0.0, grade="asymmetric",
            firing_count=0, error=str(exc)
        )

    minutes = _firing_minutes(expr)
    n = len(minutes)
    if n == 0:
        return SymmetryScoreResult(
            expression=expression, score=0.0, grade="asymmetric",
            firing_count=0, error="no firing minutes"
        )

    if n == 1:
        score = 0.0
    else:
        intervals = [minutes[i + 1] - minutes[i] for i in range(len(minutes) - 1)]
        mean_interval = sum(intervals) / len(intervals)
        if mean_interval == 0:
            score = 1.0
        else:
            variance = sum((iv - mean_interval) ** 2 for iv in intervals) / len(intervals)
            cv = (variance ** 0.5) / mean_interval
            score = max(0.0, 1.0 - min(cv, 1.0))

    return SymmetryScoreResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        firing_count=n,
    )
