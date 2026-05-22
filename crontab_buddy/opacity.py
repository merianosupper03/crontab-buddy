"""Opacity: measures how opaque/transparent a cron expression is to human readers.

Highly specific expressions (exact values) are considered opaque;
wildcard-heavy expressions are transparent.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError

_GRADES = [
    (0.85, "transparent"),
    (0.65, "translucent"),
    (0.45, "hazy"),
    (0.25, "murky"),
    (0.0,  "opaque"),
]


def _grade(score: float) -> str:
    for threshold, label in _GRADES:
        if score >= threshold:
            return label
    return "opaque"


def _field_opacity(field_str: str) -> float:
    """Return 0.0 (fully opaque) to 1.0 (fully transparent) for a single field."""
    if field_str == "*":
        return 1.0
    if field_str.startswith("*/"):
        try:
            step = int(field_str[2:])
            return min(1.0, step / 60.0) * 0.7
        except ValueError:
            return 0.5
    if "," in field_str:
        parts = field_str.split(",")
        return max(0.0, 0.8 - len(parts) * 0.1)
    if "-" in field_str:
        try:
            lo, hi = field_str.split("-", 1)
            span = int(hi) - int(lo)
            return min(0.7, span / 60.0)
        except ValueError:
            return 0.4
    # plain integer — most opaque
    return 0.0


@dataclass
class OpacityResult:
    expression: str
    score: float
    grade: str
    scores: dict = field(default_factory=dict)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"OpacityResult(error={self.error})"
        return (
            f"OpacityResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade})"
        )


def assess_opacity(expression: str) -> OpacityResult:
    """Assess the opacity of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return OpacityResult(
            expression=expression,
            score=0.0,
            grade="opaque",
            error=str(exc),
        )

    names = ["minute", "hour", "dom", "month", "dow"]
    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    scores = {name: _field_opacity(f) for name, f in zip(names, fields)}
    overall = sum(scores.values()) / len(scores)
    return OpacityResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores=scores,
    )


def batch_opacity(expressions: list[str]) -> list[OpacityResult]:
    return [assess_opacity(e) for e in expressions]
