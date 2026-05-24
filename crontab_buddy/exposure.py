"""Exposure: measures how 'exposed' a cron expression is in terms of time coverage.

A fully exposed expression (e.g. '* * * * *') fires every minute of every day,
while a minimal expression fires at a single precise moment.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.9:
        return "total"
    if score >= 0.7:
        return "high"
    if score >= 0.5:
        return "moderate"
    if score >= 0.3:
        return "low"
    if score >= 0.1:
        return "minimal"
    return "pinpoint"


def _field_exposure(value: str, field_range: int) -> float:
    """Return a 0..1 exposure score for a single field."""
    if value == "*":
        return 1.0
    if "," in value:
        parts = value.split(",")
        return min(len(parts) / field_range, 1.0)
    if "-" in value:
        lo, hi = value.split("-", 1)
        try:
            span = int(hi) - int(lo) + 1
            return min(span / field_range, 1.0)
        except ValueError:
            return 0.1
    if "/" in value:
        base, step = value.split("/", 1)
        try:
            s = int(step)
            return min((field_range / max(s, 1)) / field_range, 1.0)
        except ValueError:
            return 0.5
    return 1.0 / field_range


@dataclass
class ExposureResult:
    expression: str
    score: float
    grade: str
    scores: dict
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"ExposureResult(error={self.error})"
        return f"ExposureResult({self.expression!r}, score={self.score:.3f}, grade={self.grade})"


def assess_exposure(expression: str) -> ExposureResult:
    """Assess the temporal exposure of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ExposureResult(
            expression=expression,
            score=0.0,
            grade="pinpoint",
            scores={},
            error=str(exc),
        )

    ranges = [60, 24, 31, 12, 7]
    names = ["minute", "hour", "dom", "month", "dow"]
    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]

    field_scores = {
        name: _field_exposure(val, rng)
        for name, val, rng in zip(names, fields, ranges)
    }

    overall = sum(field_scores.values()) / len(field_scores)
    return ExposureResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores=field_scores,
    )


def batch_exposure(expressions: list[str]) -> list[ExposureResult]:
    return [assess_exposure(e) for e in expressions]
