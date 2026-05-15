"""Viscosity: measures how 'sticky' or 'resistant to change' a cron schedule feels
based on how tightly constrained its fields are."""

from dataclasses import dataclass, field
from typing import Dict, Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "rigid"
    if score >= 0.65:
        return "thick"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "fluid"
    return "free-flowing"


def _field_viscosity(value: str) -> float:
    """Return a viscosity score [0.0, 1.0] for a single cron field."""
    if value == "*":
        return 0.0
    if "," in value:
        parts = value.split(",")
        return min(0.5 + len(parts) * 0.05, 0.75)
    if "-" in value and "/" not in value:
        return 0.55
    if value.startswith("*/"):
        try:
            step = int(value[2:])
            return max(0.1, 1.0 - step / 60.0)
        except ValueError:
            return 0.3
    if "/" in value:
        return 0.4
    try:
        int(value)
        return 1.0
    except ValueError:
        return 0.5


@dataclass
class ViscosityResult:
    expression: str
    score: float
    grade: str
    scores: Dict[str, float]
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"ViscosityResult(error={self.error})"
        return (
            f"ViscosityResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r})"
        )


def assess_viscosity(expression: str) -> ViscosityResult:
    """Assess the viscosity of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ViscosityResult(
            expression=expression,
            score=0.0,
            grade="free-flowing",
            scores={},
            error=str(exc),
        )

    names = ["minute", "hour", "dom", "month", "dow"]
    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    scores = {name: _field_viscosity(val) for name, val in zip(names, fields)}
    overall = sum(scores.values()) / len(scores)
    return ViscosityResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores={k: round(v, 4) for k, v in scores.items()},
    )


def batch_viscosity(expressions: list) -> list:
    return [assess_viscosity(e) for e in expressions]
