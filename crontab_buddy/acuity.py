"""Acuity: measures how precisely targeted a cron expression is in time.

Higher acuity = more specific/pinpointed scheduling.
Lower acuity = broad/sweeping scheduling (wildcards everywhere).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


_FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]
_FIELD_RANGES = [60, 24, 31, 12, 7]


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


def _field_acuity(token: str, field_range: int) -> float:
    """Return a 0-1 acuity score for a single field token."""
    if token == "*":
        return 0.0
    if token.isdigit():
        return 1.0
    if "," in token:
        parts = token.split(",")
        return min(1.0, len(parts) / field_range * 2)
    if "-" in token and "/" not in token:
        lo, hi = token.split("-", 1)
        try:
            span = int(hi) - int(lo) + 1
            return max(0.0, 1.0 - span / field_range)
        except ValueError:
            return 0.5
    if token.startswith("*/"):
        try:
            step = int(token[2:])
            return min(1.0, step / field_range)
        except ValueError:
            return 0.3
    if "/" in token:
        return 0.4
    return 0.5


@dataclass
class AcuityResult:
    expression: str
    score: float
    grade: str
    scores: dict = field(default_factory=dict)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"AcuityResult(expression={self.expression!r}, error={self.error!r})"
        return (
            f"AcuityResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r})"
        )


def assess_acuity(expression: str) -> AcuityResult:
    """Assess the acuity of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return AcuityResult(
            expression=expression,
            score=0.0,
            grade="diffuse",
            error=str(exc),
        )

    tokens = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    per_field = {
        name: _field_acuity(tok, rng)
        for name, tok, rng in zip(_FIELD_NAMES, tokens, _FIELD_RANGES)
    }
    avg = sum(per_field.values()) / len(per_field)
    return AcuityResult(
        expression=expression,
        score=round(avg, 4),
        grade=_grade(avg),
        scores=per_field,
    )


def batch_acuity(expressions: list[str]) -> list[AcuityResult]:
    return [assess_acuity(e) for e in expressions]
