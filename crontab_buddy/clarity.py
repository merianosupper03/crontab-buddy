"""Clarity: measures how readable/understandable a cron expression is."""

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class ClarityResult:
    expression: str
    score: float  # 0.0 (opaque) to 1.0 (crystal clear)
    grade: str
    hints: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"Clarity({self.expression!r}): ERROR — {self.error}"
        return (
            f"Clarity({self.expression!r}): {self.grade} "
            f"(score={self.score:.2f})"
        )


def _grade(score: float) -> str:
    if score >= 0.85:
        return "crystal"
    if score >= 0.65:
        return "clear"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "murky"
    return "opaque"


def _field_clarity(value: str) -> float:
    """Score a single field for clarity (higher = easier to read)."""
    if value == "*":
        return 1.0
    # plain integer — very clear
    if value.isdigit():
        return 1.0
    # step on wildcard like */5 — reasonably clear
    if value.startswith("*/"):
        step = value[2:]
        return 0.75 if step.isdigit() else 0.4
    # range like 9-17
    if "-" in value and "/" not in value and "," not in value:
        return 0.65
    # list like 1,15,30
    if "," in value:
        parts = value.split(",")
        return max(0.2, 0.55 - 0.05 * max(0, len(parts) - 3))
    # step on range like 0-59/5
    if "/" in value:
        return 0.45
    return 0.3


def assess_clarity(expression: str) -> ClarityResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ClarityResult(
            expression=expression,
            score=0.0,
            grade="opaque",
            error=str(exc),
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    scores = [_field_clarity(f) for f in fields]
    score = sum(scores) / len(scores)

    hints: List[str] = []
    if expr.dom != "*" and expr.dow != "*":
        hints.append("Both DOM and DOW are set — can be confusing.")
    for f in fields:
        if "," in f and len(f.split(",")) > 5:
            hints.append(f"Field '{f}' has many list items; consider a range or step.")
            break

    return ClarityResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        hints=hints,
    )
