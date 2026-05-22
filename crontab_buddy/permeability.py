"""Permeability: measures how open/flexible a cron expression is across time dimensions."""

from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "permeable"
    if score >= 0.65:
        return "semi-permeable"
    if score >= 0.40:
        return "restrictive"
    if score >= 0.20:
        return "dense"
    return "impermeable"


def _field_permeability(field: str, max_val: int) -> float:
    """Return 0.0 (fully fixed) to 1.0 (fully open) for a single field."""
    if field == "*":
        return 1.0
    if field.startswith("*/"):
        try:
            step = int(field[2:])
            return min(1.0, (max_val / max(step, 1)) / max_val)
        except ValueError:
            return 0.5
    if "," in field:
        parts = field.split(",")
        return min(1.0, len(parts) / max_val)
    if "-" in field:
        try:
            lo, hi = field.split("-", 1)
            span = int(hi) - int(lo) + 1
            return min(1.0, span / max_val)
        except ValueError:
            return 0.3
    return 0.0  # exact value


class PermeabilityResult:
    def __init__(self, expression: str, score: float, grade: str,
                 scores: dict, error: Optional[str] = None):
        self.expression = expression
        self.score = score
        self.grade = grade
        self.scores = scores
        self.error = error

    def __str__(self) -> str:
        if self.error:
            return f"PermeabilityResult({self.expression!r}, error={self.error!r})"
        return (f"PermeabilityResult({self.expression!r}, "
                f"score={self.score:.3f}, grade={self.grade!r})")


def assess_permeability(expression: str) -> PermeabilityResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return PermeabilityResult(expression, 0.0, "impermeable", {}, error=str(exc))

    maxes = [59, 23, 31, 12, 7]
    names = ["minute", "hour", "dom", "month", "dow"]
    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]

    scores = {
        name: round(_field_permeability(f, mx), 4)
        for name, f, mx in zip(names, fields, maxes)
    }
    overall = round(sum(scores.values()) / len(scores), 4)
    return PermeabilityResult(expression, overall, _grade(overall), scores)


def batch_permeability(expressions: list) -> list:
    return [assess_permeability(e) for e in expressions]
