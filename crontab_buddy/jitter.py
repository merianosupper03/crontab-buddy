"""Jitter analysis for cron expressions.

Estimates how much randomness/spread a cron expression has relative
to a perfectly deterministic schedule.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class JitterResult:
    expression: str
    score: float  # 0.0 = no jitter (deterministic), 1.0 = maximum jitter
    label: str
    fields_contributing: List[str]
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"JitterResult(error={self.error})"
        parts = ", ".join(self.fields_contributing) if self.fields_contributing else "none"
        return f"JitterResult(score={self.score:.2f}, label={self.label}, contributors=[{parts}])"


def _grade(score: float) -> str:
    if score == 0.0:
        return "fixed"
    if score < 0.2:
        return "minimal"
    if score < 0.4:
        return "low"
    if score < 0.6:
        return "moderate"
    if score < 0.8:
        return "high"
    return "chaotic"


def _field_jitter(value: str) -> float:
    """Return a jitter contribution score for a single cron field."""
    if value == "*":
        return 1.0
    if "," in value:
        parts = value.split(",")
        return min(1.0, len(parts) / 10.0)
    if "-" in value and "/" not in value:
        lo, hi = value.split("-", 1)
        try:
            span = int(hi) - int(lo)
            return min(1.0, span / 60.0)
        except ValueError:
            return 0.5
    if value.startswith("*/") or ("/" in value):
        try:
            step = int(value.split("/")[-1])
            return max(0.0, 1.0 - step / 60.0)
        except ValueError:
            return 0.3
    return 0.0


def assess_jitter(expression: str) -> JitterResult:
    """Assess the jitter level of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return JitterResult(
            expression=expression,
            score=0.0,
            label="unknown",
            fields_contributing=[],
            error=str(exc),
        )

    field_names = ["minute", "hour", "dom", "month", "dow"]
    raw_fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    scores = [_field_jitter(f) for f in raw_fields]
    contributing = [name for name, s in zip(field_names, scores) if s > 0.0]
    overall = sum(scores) / len(scores)

    return JitterResult(
        expression=expression,
        score=round(overall, 4),
        label=_grade(overall),
        fields_contributing=contributing,
    )


def batch_jitter(expressions: List[str]) -> List[JitterResult]:
    """Assess jitter for a list of expressions."""
    return [assess_jitter(e) for e in expressions]
