"""Assess the rhythmic consistency of a cron expression."""

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class RhythmResult:
    expression: str
    score: float
    level: str
    intervals: List[int]
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"RhythmResult({self.expression!r}, error={self.error!r})"
        return (
            f"RhythmResult({self.expression!r}, level={self.level!r}, "
            f"score={self.score:.3f})"
        )


def _grade(score: float) -> str:
    if score >= 0.9:
        return "metronomic"
    if score >= 0.7:
        return "steady"
    if score >= 0.5:
        return "irregular"
    if score >= 0.25:
        return "erratic"
    return "chaotic"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return sorted list of minutes-of-day the expression fires (hour 0 only)."""
    minute_field = expr.fields[0]
    hour_field = expr.fields[1]

    minutes: List[int] = []
    for m in range(60):
        from crontab_buddy.scheduler import _matches_field
        if _matches_field(m, minute_field, 0, 59) and _matches_field(0, hour_field, 0, 23):
            minutes.append(m)
    return sorted(minutes)


def assess_rhythm(expression: str) -> RhythmResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return RhythmResult(
            expression=expression,
            score=0.0,
            level="chaotic",
            intervals=[],
            error=str(exc),
        )

    minutes = _firing_minutes(expr)
    if len(minutes) < 2:
        score = 1.0 if len(minutes) == 1 else 0.0
        return RhythmResult(
            expression=expression,
            score=score,
            level=_grade(score),
            intervals=[],
        )

    intervals = [minutes[i + 1] - minutes[i] for i in range(len(minutes) - 1)]
    mean = sum(intervals) / len(intervals)
    if mean == 0:
        score = 1.0
    else:
        variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
        cv = (variance ** 0.5) / mean
        score = max(0.0, min(1.0, 1.0 - cv))

    return RhythmResult(
        expression=expression,
        score=round(score, 4),
        level=_grade(score),
        intervals=intervals,
    )


def batch_rhythm(expressions: List[str]) -> List[RhythmResult]:
    return [assess_rhythm(e) for e in expressions]
