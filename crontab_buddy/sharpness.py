"""Sharpness: measures how precisely timed a cron expression is.

A sharp expression fires at very specific, narrow windows.
A blunt expression fires broadly (many wildcards, wide ranges).
"""

from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


_GRADES = [
    (0.85, "razor"),
    (0.65, "sharp"),
    (0.45, "moderate"),
    (0.25, "blunt"),
    (0.0,  "dull"),
]


def _grade(score: float) -> str:
    for threshold, label in _GRADES:
        if score >= threshold:
            return label
    return "dull"


def _field_sharpness(value: str, max_val: int) -> float:
    """Return 0.0 (blunt) to 1.0 (sharp) for a single field token."""
    if value == "*":
        return 0.0
    if value.isdigit():
        return 1.0
    if "," in value:
        parts = value.split(",")
        return min(1.0, len(parts) / max_val)
    if "-" in value and "/" not in value:
        lo, hi = value.split("-", 1)
        span = int(hi) - int(lo) + 1
        return max(0.0, 1.0 - span / max_val)
    if value.startswith("*/"):
        step = int(value[2:])
        return min(1.0, step / max_val)
    if "/" in value:
        base, step = value.split("/", 1)
        return min(1.0, int(step) / max_val)
    return 0.5


@dataclass
class SharpnessResult:
    expression: str
    score: float
    grade: str
    scores: dict
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"SharpnessResult(error={self.error})"
        return (
            f"SharpnessResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade})"
        )


def assess_sharpness(expression: str) -> SharpnessResult:
    """Assess the sharpness of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return SharpnessResult(
            expression=expression,
            score=0.0,
            grade="dull",
            scores={},
            error=str(exc),
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    maxes  = [59, 23, 31, 12, 7]
    names  = ["minute", "hour", "dom", "month", "dow"]

    raw_scores = {
        name: _field_sharpness(val, mx)
        for name, val, mx in zip(names, fields, maxes)
    }
    overall = sum(raw_scores.values()) / len(raw_scores)

    return SharpnessResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores={k: round(v, 4) for k, v in raw_scores.items()},
    )


def batch_sharpness(expressions: list) -> list:
    """Assess sharpness for a list of expressions."""
    return [assess_sharpness(e) for e in expressions]
