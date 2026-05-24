"""Dominance: measures how much a cron expression 'dominates' a time window
by firing relative to the maximum possible firings."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError

_MAX_DAILY_MINUTES = 1440


def _grade(score: float) -> str:
    if score >= 0.95:
        return "overwhelming"
    if score >= 0.75:
        return "dominant"
    if score >= 0.50:
        return "prominent"
    if score >= 0.25:
        return "moderate"
    if score >= 0.10:
        return "minor"
    return "negligible"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Expand the minute field to a list of matching minute values (0-59)."""
    raw = expr.fields[0]
    if raw == "*":
        return list(range(60))
    minutes: List[int] = []
    for part in raw.split(","):
        if "-" in part and "/" not in part:
            a, b = part.split("-", 1)
            minutes.extend(range(int(a), int(b) + 1))
        elif part.startswith("*/"):
            step = int(part[2:])
            minutes.extend(range(0, 60, step))
        elif "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            minutes.extend(range(start, 60, int(step)))
        else:
            minutes.append(int(part))
    return sorted(set(minutes))


def _firing_hours(expr: CronExpression) -> List[int]:
    raw = expr.fields[1]
    if raw == "*":
        return list(range(24))
    hours: List[int] = []
    for part in raw.split(","):
        if "-" in part and "/" not in part:
            a, b = part.split("-", 1)
            hours.extend(range(int(a), int(b) + 1))
        elif part.startswith("*/"):
            step = int(part[2:])
            hours.extend(range(0, 24, step))
        elif "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            hours.extend(range(start, 24, int(step)))
        else:
            hours.append(int(part))
    return sorted(set(hours))


@dataclass
class DominanceResult:
    expression: str
    score: float
    grade: str
    fires_per_day: int
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"DominanceResult(error={self.error!r})"
        return (
            f"DominanceResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r}, "
            f"fires_per_day={self.fires_per_day})"
        )


def assess_dominance(expression: str) -> DominanceResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return DominanceResult(
            expression=expression,
            score=0.0,
            grade="negligible",
            fires_per_day=0,
            error=str(exc),
        )
    mins = _firing_minutes(expr)
    hrs = _firing_hours(expr)
    fires = len(mins) * len(hrs)
    score = min(fires / _MAX_DAILY_MINUTES, 1.0)
    return DominanceResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        fires_per_day=fires,
    )


def batch_dominance(expressions: List[str]) -> List[DominanceResult]:
    return [assess_dominance(e) for e in expressions]
