"""Assess the temporal spacing between firing times of a cron expression."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.9:
        return "equidistant"
    if score >= 0.75:
        return "well-spaced"
    if score >= 0.55:
        return "moderate"
    if score >= 0.35:
        return "uneven"
    if score >= 0.15:
        return "clustered"
    return "erratic"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return sorted list of distinct minutes-of-day the expression fires."""
    minute_field = expr.fields[0]
    hour_field = expr.fields[1]

    def expand(field_str: str, max_val: int) -> List[int]:
        if field_str == "*":
            return list(range(max_val))
        values: List[int] = []
        for part in field_str.split(","):
            if "/" in part:
                base, step = part.split("/", 1)
                start = 0 if base == "*" else int(base)
                values.extend(range(start, max_val, int(step)))
            elif "-" in part:
                lo, hi = part.split("-", 1)
                values.extend(range(int(lo), int(hi) + 1))
            else:
                values.append(int(part))
        return values

    minutes = expand(minute_field, 60)
    hours = expand(hour_field, 24)
    result = sorted({h * 60 + m for h in hours for m in minutes})
    return result


@dataclass
class SpacingResult:
    expression: str
    score: float
    grade: str
    intervals: List[int] = field(default_factory=list)
    mean_interval: float = 0.0
    std_interval: float = 0.0
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"SpacingResult({self.expression!r}, error={self.error!r})"
        return (
            f"SpacingResult({self.expression!r}, grade={self.grade!r}, "
            f"score={self.score:.3f}, mean_interval={self.mean_interval:.1f}min)"
        )


def assess_spacing(expression: str) -> SpacingResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return SpacingResult(expression=expression, score=0.0, grade="erratic", error=str(exc))

    minutes = _firing_minutes(expr)
    if len(minutes) < 2:
        return SpacingResult(
            expression=expression, score=1.0, grade="equidistant",
            intervals=[], mean_interval=0.0, std_interval=0.0
        )

    intervals = [minutes[i + 1] - minutes[i] for i in range(len(minutes) - 1)]
    mean = sum(intervals) / len(intervals)
    variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
    std = variance ** 0.5

    score = 1.0 / (1.0 + std / max(mean, 1))
    return SpacingResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        intervals=intervals,
        mean_interval=round(mean, 2),
        std_interval=round(std, 2),
    )


def batch_spacing(expressions: List[str]) -> List[SpacingResult]:
    return [assess_spacing(e) for e in expressions]
