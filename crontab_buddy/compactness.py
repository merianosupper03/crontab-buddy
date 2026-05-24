"""Compactness: measures how concise/terse a cron expression is.

Higher compactness = more wildcards and less explicit values (shorter to write).
Lower compactness = more specific fields, lists, ranges (more verbose).
"""

from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "terse"
    if score >= 0.65:
        return "compact"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "verbose"
    return "exhaustive"


def _field_compactness(field_str: str) -> float:
    """Return a 0..1 compactness score for a single field token."""
    if field_str == "*":
        return 1.0
    if field_str.startswith("*/"):
        return 0.7
    if "," in field_str:
        parts = field_str.split(",")
        return max(0.0, 0.5 - 0.05 * len(parts))
    if "-" in field_str:
        return 0.4
    if "/" in field_str:
        return 0.6
    # plain integer
    return 0.2


@dataclass
class CompactnessResult:
    expression: str
    score: float
    grade: str
    scores: dict
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"CompactnessResult(error={self.error})"
        return (
            f"CompactnessResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade})"
        )


def assess_compactness(expression: str) -> CompactnessResult:
    """Assess the compactness of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return CompactnessResult(
            expression=expression,
            score=0.0,
            grade="exhaustive",
            scores={},
            error=str(exc),
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]
    field_scores = {name: _field_compactness(f) for name, f in zip(names, fields)}
    overall = sum(field_scores.values()) / len(field_scores)
    return CompactnessResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores=field_scores,
    )


def batch_compactness(expressions: list) -> list:
    return [assess_compactness(e) for e in expressions]
