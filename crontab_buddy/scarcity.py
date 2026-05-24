"""Scarcity analysis: how rarely a cron expression fires relative to the maximum possible frequency."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError

_MINUTES_PER_DAY = 1440


def _grade(score: float) -> str:
    if score >= 0.95:
        return "abundant"
    if score >= 0.75:
        return "plentiful"
    if score >= 0.50:
        return "moderate"
    if score >= 0.25:
        return "scarce"
    if score >= 0.05:
        return "rare"
    return "elusive"


def _count_firing_minutes(expr: CronExpression) -> int:
    """Estimate unique firing minutes per day."""
    def expand(field_val: str, lo: int, hi: int) -> set:
        vals: set = set()
        for part in field_val.split(","):
            if part == "*":
                vals.update(range(lo, hi + 1))
            elif "/" in part:
                base, step = part.split("/", 1)
                start = lo if base == "*" else int(base)
                vals.update(range(start, hi + 1, int(step)))
            elif "-" in part:
                a, b = part.split("-", 1)
                vals.update(range(int(a), int(b) + 1))
            else:
                vals.add(int(part))
        return vals

    minutes = expand(expr.minute, 0, 59)
    hours = expand(expr.hour, 0, 23)
    return len(minutes) * len(hours)


@dataclass
class ScarcityResult:
    expression: str
    firing_minutes: int
    score: float
    grade: str
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"ScarcityResult(error={self.error})"
        return (
            f"ScarcityResult(expression={self.expression!r}, "
            f"firing_minutes={self.firing_minutes}, "
            f"score={self.score:.3f}, grade={self.grade})"
        )


def assess_scarcity(expression: str) -> ScarcityResult:
    """Assess how scarce (infrequent) a cron expression is."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ScarcityResult(
            expression=expression,
            firing_minutes=0,
            score=0.0,
            grade="elusive",
            error=str(exc),
        )
    firing = _count_firing_minutes(expr)
    score = firing / _MINUTES_PER_DAY
    return ScarcityResult(
        expression=expression,
        firing_minutes=firing,
        score=round(score, 4),
        grade=_grade(score),
    )


def batch_scarcity(expressions: list[str]) -> list[ScarcityResult]:
    return [assess_scarcity(e) for e in expressions]
