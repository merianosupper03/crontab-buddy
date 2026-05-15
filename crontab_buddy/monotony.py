"""Monotony analysis: detect how repetitive/unchanging a cron expression is."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.9:
        return "numbing"
    if score >= 0.7:
        return "repetitive"
    if score >= 0.5:
        return "routine"
    if score >= 0.3:
        return "varied"
    return "dynamic"


def _field_monotony(value: str) -> float:
    """Return a monotony score [0, 1] for a single cron field.
    Wildcards and simple integers are maximally monotonous.
    Lists, ranges, and steps reduce monotony.
    """
    if value == "*":
        return 1.0
    if value.isdigit():
        return 1.0
    if "," in value:
        parts = value.split(",")
        return max(0.0, 1.0 - len(parts) * 0.15)
    if "-" in value and "/" not in value:
        lo, hi = value.split("-", 1)
        try:
            span = int(hi) - int(lo)
            return max(0.0, 1.0 - span * 0.05)
        except ValueError:
            return 0.5
    if "/" in value:
        base, step = value.split("/", 1)
        try:
            s = int(step)
            return max(0.0, 1.0 - 1.0 / max(s, 1) * 0.5)
        except ValueError:
            return 0.5
    return 0.5


@dataclass
class MonotonyResult:
    expression: str
    score: float
    grade: str
    scores: dict = field(default_factory=dict)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"MonotonyResult(error={self.error})"
        return f"MonotonyResult({self.expression!r}, score={self.score:.3f}, grade={self.grade!r})"


def assess_monotony(expression: str) -> MonotonyResult:
    """Assess the monotony of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return MonotonyResult(
            expression=expression,
            score=0.0,
            grade="dynamic",
            error=str(exc),
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]
    field_scores = {name: _field_monotony(val) for name, val in zip(names, fields)}
    overall = sum(field_scores.values()) / len(field_scores)
    return MonotonyResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores=field_scores,
    )


def batch_monotony(expressions: list[str]) -> list[MonotonyResult]:
    return [assess_monotony(e) for e in expressions]
