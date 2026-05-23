"""Friction score: composite measure of how 'hard' a cron expression is to reason about."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from crontab_buddy.parser import CronExpression, CronParseError


_GRADES = [
    (0.80, "impenetrable"),
    (0.60, "dense"),
    (0.40, "moderate"),
    (0.20, "manageable"),
    (0.00, "smooth"),
]


def _grade(score: float) -> str:
    for threshold, label in _GRADES:
        if score >= threshold:
            return label
    return "smooth"


def _field_friction_score(value: str) -> float:
    """Return a 0-1 friction contribution for a single field token."""
    if value == "*":
        return 0.0
    if "," in value:
        parts = value.split(",")
        return min(1.0, 0.2 + 0.1 * len(parts))
    if "/" in value:
        base, step = value.split("/", 1)
        try:
            s = int(step)
            return 0.1 if s > 1 else 0.4
        except ValueError:
            return 0.5
    if "-" in value:
        return 0.3
    try:
        int(value)
        return 0.05
    except ValueError:
        return 0.5


@dataclass
class FrictionScoreResult:
    expression: str
    score: float
    grade: str
    scores: dict
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"FrictionScore({self.expression!r}) error={self.error}"
        return (
            f"FrictionScore({self.expression!r}) "
            f"score={self.score:.3f} grade={self.grade}"
        )


def compute_friction_score(expression: str) -> FrictionScoreResult:
    """Compute composite friction score for a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return FrictionScoreResult(
            expression=expression,
            score=1.0,
            grade="impenetrable",
            scores={},
            error=str(exc),
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]
    weights = [0.25, 0.25, 0.20, 0.15, 0.15]

    scores = {}
    total = 0.0
    for name, val, w in zip(names, fields, weights):
        s = _field_friction_score(val)
        scores[name] = round(s, 4)
        total += s * w

    total = round(min(1.0, total), 4)
    return FrictionScoreResult(
        expression=expression,
        score=total,
        grade=_grade(total),
        scores=scores,
    )
