"""Intensity: measures how aggressively a cron expression fires relative to its time window."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.9:
        return "overwhelming"
    if score >= 0.7:
        return "intense"
    if score >= 0.5:
        return "moderate"
    if score >= 0.3:
        return "mild"
    if score >= 0.1:
        return "faint"
    return "negligible"


def _firing_minutes(expr: CronExpression) -> list[int]:
    minute = expr.fields[0]
    if minute == "*":
        return list(range(60))
    if "/" in minute:
        parts = minute.split("/")
        step = int(parts[1])
        start = 0 if parts[0] == "*" else int(parts[0])
        return list(range(start, 60, step))
    if "-" in minute:
        lo, hi = minute.split("-")
        return list(range(int(lo), int(hi) + 1))
    if "," in minute:
        return [int(v) for v in minute.split(",")]
    return [int(minute)]


def _firing_hours(expr: CronExpression) -> list[int]:
    hour = expr.fields[1]
    if hour == "*":
        return list(range(24))
    if "/" in hour:
        parts = hour.split("/")
        step = int(parts[1])
        start = 0 if parts[0] == "*" else int(parts[0])
        return list(range(start, 24, step))
    if "-" in hour:
        lo, hi = hour.split("-")
        return list(range(int(lo), int(hi) + 1))
    if "," in hour:
        return [int(v) for v in hour.split(",")]
    return [int(hour)]


@dataclass
class IntensityResult:
    expression: str
    score: float
    grade: str
    runs_per_day: int
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"IntensityResult(error={self.error})"
        return (
            f"IntensityResult(expression={self.expression!r}, "
            f"grade={self.grade!r}, score={self.score:.3f}, "
            f"runs_per_day={self.runs_per_day})"
        )


def assess_intensity(expression: str) -> IntensityResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return IntensityResult(expression=expression, score=0.0, grade="negligible", runs_per_day=0, error=str(exc))

    minutes = _firing_minutes(expr)
    hours = _firing_hours(expr)
    runs_per_day = len(minutes) * len(hours)
    max_per_day = 1440
    score = min(runs_per_day / max_per_day, 1.0)
    return IntensityResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        runs_per_day=runs_per_day,
    )


def batch_intensity(expressions: list[str]) -> list[IntensityResult]:
    return [assess_intensity(e) for e in expressions]
