"""Rigidity assessment for cron expressions.

Measures how inflexible or tightly constrained a cron expression is.
Highly rigid expressions fire at exact, narrow windows; flexible ones
use wildcards or broad ranges.
"""

from crontab_buddy.parser import CronExpression, CronParseError

_FIELD_RANGES = [59, 23, 31, 12, 7]


def _grade(score: float) -> str:
    if score >= 0.85:
        return "ironclad"
    if score >= 0.65:
        return "rigid"
    if score >= 0.45:
        return "firm"
    if score >= 0.25:
        return "pliable"
    return "supple"


def _field_rigidity(field: str, max_val: int) -> float:
    """Return a rigidity score [0, 1] for a single field."""
    if field == "*":
        return 0.0
    if field.lstrip("-0123456789").startswith("/"):
        # step: */N — higher N means fewer firings → more rigid
        try:
            step = int(field.split("/")[1])
            return min(1.0, step / max_val)
        except (IndexError, ValueError):
            return 0.5
    if "-" in field:
        parts = field.split("-")
        try:
            lo, hi = int(parts[0]), int(parts[1])
            span = (hi - lo + 1) / (max_val + 1)
            return max(0.0, 1.0 - span)
        except (IndexError, ValueError):
            return 0.5
    if "," in field:
        count = len(field.split(","))
        return max(0.0, 1.0 - count / (max_val + 1))
    # plain integer — maximally rigid
    return 1.0


class RigidityResult:
    def __init__(self, expression: str, score: float, scores: dict,
                 grade: str, error: str = ""):
        self.expression = expression
        self.score = round(score, 4)
        self.scores = scores
        self.grade = grade
        self.error = error

    def __str__(self) -> str:
        if self.error:
            return f"RigidityResult(error={self.error!r})"
        return (
            f"RigidityResult(expression={self.expression!r}, "
            f"score={self.score}, grade={self.grade!r})"
        )


def assess_rigidity(expression: str) -> RigidityResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return RigidityResult(expression, 0.0, {}, "unknown", error=str(exc))

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]
    scores = {}
    for name, field, max_val in zip(names, fields, _FIELD_RANGES):
        scores[name] = round(_field_rigidity(field, max_val), 4)

    overall = sum(scores.values()) / len(scores)
    return RigidityResult(
        expression=expression,
        score=overall,
        scores=scores,
        grade=_grade(overall),
    )


def batch_rigidity(expressions: list) -> list:
    return [assess_rigidity(e) for e in expressions]
