"""Tightness: measures how constrained/specific a cron expression is across all fields."""
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "ironclad"
    if score >= 0.70:
        return "tight"
    if score >= 0.50:
        return "moderate"
    if score >= 0.30:
        return "loose"
    if score >= 0.10:
        return "slack"
    return "unbounded"


def _field_tightness(field: str) -> float:
    """Return 0.0 (fully open) to 1.0 (fully constrained) for a single field."""
    if field == "*":
        return 0.0
    if "," in field:
        parts = field.split(",")
        return min(1.0, 0.4 + 0.1 * len(parts))
    if "-" in field and "/" not in field:
        lo, hi = field.split("-", 1)
        try:
            span = int(hi) - int(lo)
            return max(0.1, 1.0 - span / 60.0)
        except ValueError:
            return 0.3
    if field.startswith("*/"):
        try:
            step = int(field[2:])
            return min(0.9, step / 60.0)
        except ValueError:
            return 0.2
    if "/" in field:
        return 0.5
    try:
        int(field)
        return 1.0
    except ValueError:
        return 0.5


class TightnessResult:
    def __init__(self, expression: str, score: float, grade: str,
                 scores: dict, error: Optional[str] = None):
        self.expression = expression
        self.score = score
        self.grade = grade
        self.scores = scores
        self.error = error

    def __str__(self) -> str:
        if self.error:
            return f"TightnessResult(error={self.error})"
        return f"TightnessResult(expression={self.expression!r}, score={self.score:.3f}, grade={self.grade})"


def assess_tightness(expression: str) -> TightnessResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return TightnessResult(expression, 0.0, "unbounded", {}, error=str(exc))

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]
    scores = {name: _field_tightness(f) for name, f in zip(names, fields)}
    overall = sum(scores.values()) / len(scores)
    return TightnessResult(expression, overall, _grade(overall), scores)


def batch_tightness(expressions: list) -> list:
    return [assess_tightness(e) for e in expressions]
