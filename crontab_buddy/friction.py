"""Friction analysis: measures how hard it is to trigger an expression.

Higher friction = expression fires rarely / at very specific times.
Lower friction = expression fires often / broadly.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "rigid"
    if score >= 0.65:
        return "stiff"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "loose"
    return "frictionless"


def _field_friction(value: str, field_range: int) -> float:
    """Return a 0-1 friction score for a single field."""
    if value == "*":
        return 0.0
    if "," in value:
        parts = value.split(",")
        return max(0.0, 1.0 - len(parts) / field_range)
    if "-" in value:
        lo, hi = value.split("-", 1)
        try:
            span = int(hi) - int(lo) + 1
            return max(0.0, 1.0 - span / field_range)
        except ValueError:
            return 0.5
    if "/" in value:
        base, step = value.split("/", 1)
        try:
            return max(0.0, 1.0 - (1 / int(step)))
        except (ValueError, ZeroDivisionError):
            return 0.5
    return 1.0  # exact value


_FIELD_RANGES = [60, 24, 31, 12, 7]


@dataclass
class FrictionResult:
    expression: str
    score: float
    grade: str
    scores: dict
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"FrictionResult({self.expression!r}, error={self.error!r})"
        return f"FrictionResult({self.expression!r}, score={self.score:.3f}, grade={self.grade!r})"


def assess_friction(expression: str) -> FrictionResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return FrictionResult(
            expression=expression,
            score=0.0,
            grade="frictionless",
            scores={},
            error=str(exc),
        )
    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]
    scores = {
        name: _field_friction(fval, frange)
        for name, fval, frange in zip(names, fields, _FIELD_RANGES)
    }
    overall = sum(scores.values()) / len(scores)
    return FrictionResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores={k: round(v, 4) for k, v in scores.items()},
    )


def batch_friction(expressions: list[str]) -> list[FrictionResult]:
    return [assess_friction(e) for e in expressions]
