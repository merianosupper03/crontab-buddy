"""Burstiness analysis for cron expressions.

Measures how clustered or spread out firing times are within an hour,
using the coefficient of variation of inter-firing intervals.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class BurstinessResult:
    expression: str
    score: float  # 0.0 = perfectly uniform, 1.0 = maximally bursty
    label: str
    intervals: List[int]
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"{self.expression}: error — {self.error}"
        return (
            f"{self.expression}: burstiness={self.score:.3f} ({self.label})"
        )


def _grade(score: float) -> str:
    if score < 0.1:
        return "uniform"
    if score < 0.3:
        return "smooth"
    if score < 0.6:
        return "moderate"
    if score < 0.85:
        return "bursty"
    return "spiky"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return sorted list of minutes-within-hour the expression fires."""
    minute_field = expr.fields[0]
    if minute_field == "*":
        return list(range(60))
    minutes = []
    for part in minute_field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            minutes.extend(range(start, 60, int(step)))
        elif "-" in part:
            lo, hi = part.split("-", 1)
            minutes.extend(range(int(lo), int(hi) + 1))
        else:
            minutes.append(int(part))
    return sorted(set(minutes))


def assess_burstiness(expression: str) -> BurstinessResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return BurstinessResult(
            expression=expression,
            score=1.0,
            label="spiky",
            intervals=[],
            error=str(exc),
        )

    minutes = _firing_minutes(expr)
    if len(minutes) < 2:
        return BurstinessResult(
            expression=expression,
            score=1.0,
            label="spiky",
            intervals=[],
        )

    intervals = [
        minutes[i + 1] - minutes[i] for i in range(len(minutes) - 1)
    ]
    mean = sum(intervals) / len(intervals)
    if mean == 0:
        score = 0.0
    else:
        variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
        cv = (variance ** 0.5) / mean
        score = min(1.0, cv)

    return BurstinessResult(
        expression=expression,
        score=round(score, 4),
        label=_grade(score),
        intervals=intervals,
    )


def batch_burstiness(expressions: List[str]) -> List[BurstinessResult]:
    return [assess_burstiness(e) for e in expressions]
