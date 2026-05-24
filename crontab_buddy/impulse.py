"""Impulse: measures the 'suddenness' of a cron expression's firing pattern.

High impulse = fires in tight bursts; low impulse = fires evenly spread out.
"""

from __future__ import annotations
from typing import List, Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "explosive"
    if score >= 0.65:
        return "sharp"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "gentle"
    return "flat"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return all minutes-of-day (0..1439) when the expression fires."""
    minutes: List[int] = []
    min_field = expr.minute
    hour_field = expr.hour

    def _expand(field: str, lo: int, hi: int) -> List[int]:
        if field == "*":
            return list(range(lo, hi + 1))
        result = []
        for part in field.split(","):
            if "/" in part:
                base, step = part.split("/", 1)
                start = lo if base == "*" else int(base.split("-")[0])
                for v in range(start, hi + 1, int(step)):
                    result.append(v)
            elif "-" in part:
                a, b = part.split("-", 1)
                result.extend(range(int(a), int(b) + 1))
            else:
                result.append(int(part))
        return result

    mins = _expand(min_field, 0, 59)
    hours = _expand(hour_field, 0, 23)
    for h in hours:
        for m in mins:
            minutes.append(h * 60 + m)
    return sorted(set(minutes))


class ImpulseResult:
    def __init__(self, expression: str, score: float, grade: str,
                 firing_count: int, error: Optional[str] = None):
        self.expression = expression
        self.score = score
        self.grade = grade
        self.firing_count = firing_count
        self.error = error

    def __str__(self) -> str:
        if self.error:
            return f"ImpulseResult({self.expression!r}, error={self.error!r})"
        return (f"ImpulseResult({self.expression!r}, score={self.score:.3f}, "
                f"grade={self.grade!r}, firing_count={self.firing_count})")


def assess_impulse(expression: str) -> ImpulseResult:
    """Assess the impulse of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ImpulseResult(expression, 0.0, "flat", 0, error=str(exc))

    minutes = _firing_minutes(expr)
    total = len(minutes)
    if total == 0:
        return ImpulseResult(expression, 0.0, "flat", 0)

    if total == 1:
        return ImpulseResult(expression, 1.0, "explosive", 1)

    intervals = [minutes[i + 1] - minutes[i] for i in range(len(minutes) - 1)]
    mean_interval = sum(intervals) / len(intervals)
    variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)

    max_possible_variance = (720.0) ** 2
    raw_score = min(variance / max_possible_variance, 1.0) ** 0.5
    score = round(raw_score, 4)
    return ImpulseResult(expression, score, _grade(score), total)


def batch_impulse(expressions: List[str]) -> List[ImpulseResult]:
    return [assess_impulse(e) for e in expressions]
