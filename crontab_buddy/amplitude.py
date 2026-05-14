"""Amplitude analysis: measures the intensity range of a cron expression."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


DEFAULT_RANGES = {
    "minute": 60,
    "hour": 24,
    "dom": 31,
    "month": 12,
    "dow": 7,
}


def _grade(score: float) -> str:
    if score >= 0.85:
        return "maximal"
    if score >= 0.65:
        return "high"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "low"
    return "minimal"


def _field_amplitude(value: str, total: int) -> float:
    if value == "*":
        return 1.0
    if "," in value:
        parts = value.split(",")
        return min(len(parts) / total, 1.0)
    if "-" in value:
        lo, hi = value.split("-", 1)
        try:
            return min((int(hi) - int(lo) + 1) / total, 1.0)
        except ValueError:
            return 0.1
    if "/" in value:
        base, step = value.split("/", 1)
        try:
            s = int(step)
            return min((total / max(s, 1)) / total, 1.0)
        except ValueError:
            return 0.1
    return 1.0 / total


@dataclass
class AmplitudeResult:
    expression: str
    score: float
    grade: str
    scores: dict = field(default_factory=dict)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"AmplitudeResult(error={self.error})"
        return f"AmplitudeResult({self.expression!r}, score={self.score:.3f}, grade={self.grade})"


def assess_amplitude(expression: str) -> AmplitudeResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return AmplitudeResult(expression=expression, score=0.0, grade="minimal", error=str(exc))

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = list(DEFAULT_RANGES.keys())
    totals = list(DEFAULT_RANGES.values())

    scores = {name: _field_amplitude(val, tot) for name, val, tot in zip(names, fields, totals)}
    overall = sum(scores.values()) / len(scores)

    return AmplitudeResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores=scores,
    )


def batch_amplitude(expressions: list[str]) -> list[AmplitudeResult]:
    return [assess_amplitude(e) for e in expressions]
