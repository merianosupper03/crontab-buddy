"""Clutter: measures how 'busy' or visually complex a cron expression is."""

from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "chaotic"
    if score >= 0.65:
        return "cluttered"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "tidy"
    return "minimal"


def _field_clutter(field_str: str) -> float:
    """Score a single field for visual clutter (0=clean, 1=messy)."""
    if field_str == "*":
        return 0.0
    if "," in field_str:
        parts = field_str.split(",")
        return min(1.0, 0.3 + 0.15 * len(parts))
    if "-" in field_str and "/" in field_str:
        return 0.7
    if "-" in field_str:
        return 0.4
    if field_str.startswith("*/"):
        return 0.2
    if "/" in field_str:
        return 0.5
    return 0.1


@dataclass
class ClutterResult:
    expression: str
    score: float
    grade: str
    scores: dict
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"ClutterResult({self.expression!r}, error={self.error!r})"
        return f"ClutterResult({self.expression!r}, grade={self.grade!r}, score={self.score:.3f})"


def assess_clutter(expression: str) -> ClutterResult:
    """Assess the visual clutter of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ClutterResult(
            expression=expression,
            score=1.0,
            grade="chaotic",
            scores={},
            error=str(exc),
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]
    scores = {name: _field_clutter(f) for name, f in zip(names, fields)}
    avg = sum(scores.values()) / len(scores)
    return ClutterResult(
        expression=expression,
        score=round(avg, 4),
        grade=_grade(avg),
        scores=scores,
    )


def batch_clutter(expressions: list) -> list:
    return [assess_clutter(e) for e in expressions]
