"""Smoothness assessment for cron expressions.

Measures how gradually a cron expression distributes its firing minutes
across an hour. High smoothness = evenly spread, low = clustered/spiky.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.9:
        return "silky"
    if score >= 0.75:
        return "smooth"
    if score >= 0.55:
        return "moderate"
    if score >= 0.35:
        return "rough"
    return "jagged"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return sorted list of unique firing minutes within [0, 59]."""
    minute_field = expr.fields[0]
    if minute_field == "*":
        return list(range(60))
    minutes: List[int] = []
    for part in minute_field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            step_val = int(step)
            minutes.extend(range(start, 60, step_val))
        elif "-" in part:
            lo, hi = part.split("-", 1)
            minutes.extend(range(int(lo), int(hi) + 1))
        else:
            minutes.append(int(part))
    return sorted(set(m for m in minutes if 0 <= m <= 59))


@dataclass
class SmoothnessResult:
    expression: str
    score: float
    grade: str
    firing_minutes: List[int]
    intervals: List[int]
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"SmoothnessResult(error={self.error!r})"
        return (
            f"SmoothnessResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r})"
        )


def assess_smoothness(expression: str) -> SmoothnessResult:
    """Assess smoothness of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return SmoothnessResult(
            expression=expression,
            score=0.0,
            grade="jagged",
            firing_minutes=[],
            intervals=[],
            error=str(exc),
        )

    minutes = _firing_minutes(expr)
    if len(minutes) <= 1:
        score = 0.0
        intervals: List[int] = []
    else:
        gaps = [minutes[i + 1] - minutes[i] for i in range(len(minutes) - 1)]
        mean_gap = sum(gaps) / len(gaps)
        variance = sum((g - mean_gap) ** 2 for g in gaps) / len(gaps)
        max_variance = mean_gap ** 2
        score = 1.0 - min(variance / max_variance, 1.0) if max_variance > 0 else 1.0
        intervals = gaps

    return SmoothnessResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        firing_minutes=minutes,
        intervals=intervals,
    )


def batch_smoothness(expressions: List[str]) -> List[SmoothnessResult]:
    return [assess_smoothness(e) for e in expressions]
