"""Fuzziness: measure how ambiguous or imprecise a cron expression is."""

from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]


def _grade(score: float) -> str:
    if score >= 0.85:
        return "nebulous"
    if score >= 0.65:
        return "hazy"
    if score >= 0.45:
        return "fuzzy"
    if score >= 0.25:
        return "clear"
    return "crisp"


def _field_fuzziness(value: str) -> float:
    """Return a fuzziness score [0.0, 1.0] for a single field token."""
    if value == "*":
        return 1.0
    if "," in value:
        parts = value.split(",")
        return min(0.8, 0.4 + 0.1 * len(parts))
    if "-" in value and "/" in value:
        return 0.6
    if value.startswith("*/"):
        try:
            step = int(value[2:])
            return max(0.1, 1.0 - step / 60.0)
        except ValueError:
            return 0.5
    if "/" in value:
        return 0.55
    if "-" in value:
        lo, _, hi = value.partition("-")
        try:
            span = int(hi) - int(lo)
            return min(0.75, 0.2 + span / 60.0)
        except ValueError:
            return 0.4
    return 0.0


@dataclass
class FuzzinessResult:
    expression: str
    scores: dict = field(default_factory=dict)
    overall: float = 0.0
    grade: str = ""
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"FuzzinessResult(error={self.error})"
        return (
            f"FuzzinessResult(expression={self.expression!r}, "
            f"overall={self.overall:.3f}, grade={self.grade!r})"
        )


def assess_fuzziness(expression: str) -> FuzzinessResult:
    """Assess how fuzzy/ambiguous a cron expression is."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return FuzzinessResult(expression=expression, error=str(exc))

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    scores = {name: _field_fuzziness(val) for name, val in zip(FIELD_NAMES, fields)}
    overall = sum(scores.values()) / len(scores)
    return FuzzinessResult(
        expression=expression,
        scores=scores,
        overall=round(overall, 4),
        grade=_grade(overall),
    )


def batch_fuzziness(expressions: list) -> list:
    """Assess fuzziness for a list of expressions."""
    return [assess_fuzziness(expr) for expr in expressions]
