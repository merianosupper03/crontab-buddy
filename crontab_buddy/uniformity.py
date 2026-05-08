"""Uniformity: measure how evenly a cron expression distributes its firings across time."""

from dataclasses import dataclass, field
from typing import List, Optional
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class UniformityResult:
    expression: str
    score: float  # 0.0 (clustered) to 1.0 (perfectly uniform)
    grade: str
    intervals: List[int]  # gaps in minutes between consecutive firings in a day
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"UniformityResult({self.expression!r}, error={self.error!r})"
        return (
            f"UniformityResult({self.expression!r}, score={self.score:.3f}, "
            f"grade={self.grade!r})"
        )


def _grade(score: float) -> str:
    if score >= 0.9:
        return "excellent"
    if score >= 0.7:
        return "good"
    if score >= 0.5:
        return "moderate"
    if score >= 0.25:
        return "poor"
    return "clustered"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return sorted list of minutes-of-day when the expression fires (first 1440 minutes)."""
    minutes_field = expr.fields[0]
    hours_field = expr.fields[1]

    def expand(field_str: str, max_val: int) -> List[int]:
        if field_str == "*":
            return list(range(max_val))
        values = set()
        for part in field_str.split(","):
            if "/" in part:
                base, step = part.split("/", 1)
                step = int(step)
                start = 0 if base == "*" else int(base.split("-")[0])
                end = max_val - 1 if base == "*" else (
                    int(base.split("-")[1]) if "-" in base else start
                )
                values.update(range(start, end + 1, step))
            elif "-" in part:
                a, b = part.split("-", 1)
                values.update(range(int(a), int(b) + 1))
            else:
                values.add(int(part))
        return sorted(values)

    mins = expand(minutes_field, 60)
    hrs = expand(hours_field, 24)
    result = sorted(h * 60 + m for h in hrs for m in mins)
    return result


def assess_uniformity(expression: str) -> UniformityResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return UniformityResult(
            expression=expression,
            score=0.0,
            grade="clustered",
            intervals=[],
            error=str(exc),
        )

    firings = _firing_minutes(expr)
    if len(firings) < 2:
        return UniformityResult(
            expression=expression,
            score=0.0,
            grade="clustered",
            intervals=[],
        )

    intervals = [
        firings[i + 1] - firings[i] for i in range(len(firings) - 1)
    ]
    mean = sum(intervals) / len(intervals)
    variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
    std = variance ** 0.5
    cv = std / mean if mean > 0 else 1.0
    score = max(0.0, min(1.0, 1.0 - cv))
    return UniformityResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        intervals=intervals,
    )


def batch_uniformity(expressions: List[str]) -> List[UniformityResult]:
    return [assess_uniformity(e) for e in expressions]
