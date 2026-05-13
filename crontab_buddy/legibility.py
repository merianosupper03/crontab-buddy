"""Legibility scoring for cron expressions.

Measures how easy a cron expression is to read and understand at a glance.
Higher scores mean the expression is more immediately comprehensible.
"""

from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class LegibilityResult:
    expression: str
    score: float
    grade: str
    field_scores: dict
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"LegibilityResult({self.expression!r}, error={self.error!r})"
        return (
            f"LegibilityResult({self.expression!r}, "
            f"score={self.score:.2f}, grade={self.grade!r})"
        )


def _grade(score: float) -> str:
    if score >= 0.85:
        return "transparent"
    if score >= 0.65:
        return "clear"
    if score >= 0.45:
        return "readable"
    if score >= 0.25:
        return "murky"
    return "opaque"


def _field_legibility(value: str) -> float:
    """Return a 0-1 legibility score for a single cron field token."""
    if value == "*":
        return 1.0
    # plain integer — most legible
    if value.isdigit():
        return 0.95
    # named aliases e.g. MON, JAN
    if value.isalpha():
        return 0.90
    # simple range like 9-17
    if "-" in value and "/" not in value and "," not in value:
        return 0.70
    # step on wildcard */5
    if value.startswith("*/"):
        return 0.65
    # step on range 1-5/2
    if "/" in value and "-" in value:
        return 0.40
    # list of values
    if "," in value:
        parts = value.split(",")
        avg = sum(_field_legibility(p.strip()) for p in parts) / len(parts)
        # penalise long lists
        penalty = max(0.0, (len(parts) - 3) * 0.05)
        return max(0.0, avg - penalty)
    # step on plain number — unusual
    if "/" in value:
        return 0.50
    return 0.30


def assess_legibility(expression: str) -> LegibilityResult:
    """Assess the legibility of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return LegibilityResult(
            expression=expression,
            score=0.0,
            grade="opaque",
            field_scores={},
            error=str(exc),
        )

    names = ["minute", "hour", "dom", "month", "dow"]
    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    field_scores = {name: _field_legibility(val) for name, val in zip(names, fields)}
    score = sum(field_scores.values()) / len(field_scores)
    return LegibilityResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        field_scores=field_scores,
    )
