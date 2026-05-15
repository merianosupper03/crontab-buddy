"""Specificity: measures how precisely a cron expression targets a point in time.

Higher specificity means the expression fires at very exact, narrow times.
Lower specificity means it fires broadly (e.g. every minute).
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from crontab_buddy.parser import CronExpression, CronParseError

_FIELD_RANGES = {
    "minute": 60,
    "hour": 24,
    "dom": 31,
    "month": 12,
    "dow": 7,
}


def _grade(score: float) -> str:
    if score >= 0.85:
        return "pinpoint"
    if score >= 0.65:
        return "focused"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "broad"
    return "diffuse"


def _field_specificity(value: str, total: int) -> float:
    """Return a 0..1 specificity score for a single field token."""
    if value == "*":
        return 0.0
    if value.startswith("*/"):
        try:
            step = int(value[2:])
            return 1.0 - (step / total)
        except ValueError:
            return 0.0
    if "," in value:
        count = len(value.split(","))
        return min(1.0, count / total)
    if "-" in value:
        parts = value.split("-")
        try:
            lo, hi = int(parts[0]), int(parts[1])
            span = hi - lo + 1
            return 1.0 - (span / total)
        except (ValueError, IndexError):
            return 0.0
    return 1.0


@dataclass
class SpecificityResult:
    expression: str
    score: float
    grade: str
    scores: Dict[str, float]
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"SpecificityResult(error={self.error})"
        return (
            f"SpecificityResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r})"
        )


def assess_specificity(expression: str) -> SpecificityResult:
    """Assess the specificity of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return SpecificityResult(
            expression=expression,
            score=0.0,
            grade="diffuse",
            scores={},
            error=str(exc),
        )

    fields = {
        "minute": expr.minute,
        "hour": expr.hour,
        "dom": expr.dom,
        "month": expr.month,
        "dow": expr.dow,
    }

    scores = {
        name: _field_specificity(val, _FIELD_RANGES[name])
        for name, val in fields.items()
    }

    overall = sum(scores.values()) / len(scores)
    return SpecificityResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores={k: round(v, 4) for k, v in scores.items()},
    )


def batch_specificity(expressions: list) -> list:
    """Assess specificity for a list of expressions."""
    return [assess_specificity(e) for e in expressions]
