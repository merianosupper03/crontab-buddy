"""Precision analysis for cron expressions.

Measures how precisely a cron expression targets specific points in time
vs. how broadly it fires across a time window.
"""

from dataclasses import dataclass
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class PrecisionResult:
    expression: str
    score: float  # 0.0 (broad) to 1.0 (precise)
    level: str
    description: str
    error: str = ""

    def __str__(self) -> str:
        if self.error:
            return f"PrecisionResult(error={self.error})"
        return (
            f"PrecisionResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, level={self.level!r})"
        )


def _grade(score: float) -> str:
    if score >= 0.85:
        return "exact"
    if score >= 0.65:
        return "precise"
    if score >= 0.40:
        return "moderate"
    if score >= 0.20:
        return "broad"
    return "diffuse"


def _field_precision(field: str) -> float:
    """Return a 0-1 precision score for a single cron field."""
    if field == "*":
        return 0.0
    if field.startswith("*/"):
        try:
            step = int(field[2:])
            # larger step -> more precise (fires less often)
            return min(step / 60.0, 1.0)
        except ValueError:
            return 0.1
    if "-" in field and "/" not in field:
        parts = field.split("-")
        try:
            lo, hi = int(parts[0]), int(parts[1])
            span = hi - lo + 1
            return max(0.0, 1.0 - span / 60.0)
        except (ValueError, IndexError):
            return 0.3
    if "," in field:
        count = len(field.split(","))
        return max(0.0, 1.0 - count / 10.0)
    # plain integer — most precise
    try:
        int(field)
        return 1.0
    except ValueError:
        return 0.2


def assess_precision(expression: str) -> PrecisionResult:
    """Assess the precision of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return PrecisionResult(
            expression=expression,
            score=0.0,
            level="unknown",
            description="Invalid expression.",
            error=str(exc),
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    scores = [_field_precision(f) for f in fields]
    score = sum(scores) / len(scores)
    level = _grade(score)
    description = (
        f"Expression fires with {level} precision "
        f"(score {score:.2f}/1.00)."
    )
    return PrecisionResult(
        expression=expression,
        score=round(score, 4),
        level=level,
        description=description,
    )
