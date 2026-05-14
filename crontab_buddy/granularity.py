"""Assess the granularity (time resolution) of a cron expression."""

from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


GRADE_MAP = [
    (0.85, "ultra-fine"),
    (0.65, "fine"),
    (0.45, "medium"),
    (0.25, "coarse"),
    (0.0,  "very coarse"),
]


def _grade(score: float) -> str:
    for threshold, label in GRADE_MAP:
        if score >= threshold:
            return label
    return "very coarse"


def _field_granularity(field_str: str, field_range: int) -> float:
    """Return a 0-1 score reflecting how fine-grained this field is."""
    if field_str == "*":
        return 1.0
    if field_str.startswith("*/"):
        try:
            step = int(field_str[2:])
            return max(0.0, 1.0 - (step - 1) / field_range)
        except ValueError:
            return 0.5
    if "," in field_str:
        parts = field_str.split(",")
        return min(1.0, len(parts) / field_range)
    if "-" in field_str:
        lo, _, hi = field_str.partition("-")
        try:
            span = int(hi) - int(lo) + 1
            return min(1.0, span / field_range)
        except ValueError:
            return 0.5
    return 0.2  # single exact value — very coarse


@dataclass
class GranularityResult:
    expression: str
    score: float
    grade: str
    scores: dict
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"GranularityResult(error={self.error})"
        return (
            f"GranularityResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r})"
        )


_FIELD_RANGES = [59, 23, 31, 12, 7]  # minute, hour, dom, month, dow
_FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]


def assess_granularity(expression: str) -> GranularityResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return GranularityResult(
            expression=expression,
            score=0.0,
            grade="very coarse",
            scores={},
            error=str(exc),
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    weights = [0.40, 0.30, 0.15, 0.10, 0.05]

    scores = {}
    weighted_sum = 0.0
    for name, f, r, w in zip(_FIELD_NAMES, fields, _FIELD_RANGES, weights):
        s = _field_granularity(f, r)
        scores[name] = round(s, 4)
        weighted_sum += s * w

    overall = round(weighted_sum, 4)
    return GranularityResult(
        expression=expression,
        score=overall,
        grade=_grade(overall),
        scores=scores,
    )
