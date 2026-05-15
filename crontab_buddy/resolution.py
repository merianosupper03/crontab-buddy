"""Resolution: measures how fine-grained a cron expression's scheduling is."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "atomic"
    if score >= 0.65:
        return "fine"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "coarse"
    return "blunt"


def _field_resolution(value: str, max_val: int) -> float:
    """Return a 0-1 resolution score for a single field."""
    if value == "*":
        return 1.0
    if value.startswith("*/"):
        try:
            step = int(value[2:])
            return max(0.0, 1.0 - (step - 1) / max(max_val, 1))
        except ValueError:
            return 0.5
    if "," in value:
        parts = value.split(",")
        return min(1.0, len(parts) / max(max_val, 1))
    if "-" in value:
        lo, _, hi = value.partition("-")
        try:
            span = int(hi) - int(lo) + 1
            return min(1.0, span / max(max_val, 1))
        except ValueError:
            return 0.5
    return 0.1  # exact single value — very coarse


@dataclass
class ResolutionResult:
    expression: str
    score: float
    grade: str
    scores: dict = field(default_factory=dict)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"ResolutionResult(error={self.error})"
        return (
            f"ResolutionResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r})"
        )


def assess_resolution(expression: str) -> ResolutionResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ResolutionResult(expression=expression, score=0.0, grade="blunt", error=str(exc))

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    maxes = [59, 23, 31, 12, 7]
    names = ["minute", "hour", "dom", "month", "dow"]
    weights = [0.35, 0.25, 0.20, 0.10, 0.10]

    scores = {}
    total = 0.0
    for name, val, mx, w in zip(names, fields, maxes, weights):
        s = _field_resolution(val, mx)
        scores[name] = round(s, 4)
        total += s * w

    return ResolutionResult(
        expression=expression,
        score=round(total, 4),
        grade=_grade(total),
        scores=scores,
    )


def batch_resolution(expressions: list[str]) -> list[ResolutionResult]:
    return [assess_resolution(e) for e in expressions]
