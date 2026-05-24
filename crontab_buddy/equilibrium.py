"""Equilibrium: measures how balanced a cron expression is across time dimensions."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


VALID_RANGES = {
    "minute": 60,
    "hour": 24,
    "dom": 31,
    "month": 12,
    "dow": 7,
}


def _grade(score: float) -> str:
    if score >= 0.85:
        return "harmonious"
    if score >= 0.65:
        return "balanced"
    if score >= 0.45:
        return "uneven"
    if score >= 0.25:
        return "lopsided"
    return "chaotic"


def _field_equilibrium(field_str: str, total: int) -> float:
    """Returns 0.0 (very unbalanced) to 1.0 (perfectly balanced)."""
    if field_str == "*":
        return 1.0
    if field_str.startswith("*/"):
        try:
            step = int(field_str[2:])
            return round(min(step, total) / total, 4)
        except ValueError:
            return 0.5
    if "," in field_str:
        parts = field_str.split(",")
        return round(min(len(parts) / total, 1.0), 4)
    if "-" in field_str:
        lo, _, hi = field_str.partition("-")
        try:
            span = int(hi) - int(lo) + 1
            return round(min(span / total, 1.0), 4)
        except ValueError:
            return 0.5
    return 0.1


@dataclass
class EquilibriumResult:
    expression: str
    score: float
    grade: str
    scores: dict = field(default_factory=dict)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"EquilibriumResult(error={self.error})"
        return (
            f"EquilibriumResult(expression={self.expression!r}, "
            f"score={self.score:.4f}, grade={self.grade!r})"
        )


def assess_equilibrium(expression: str) -> EquilibriumResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return EquilibriumResult(
            expression=expression, score=0.0, grade="chaotic", error=str(exc)
        )

    fields = [
        ("minute", expr.minute, 60),
        ("hour", expr.hour, 24),
        ("dom", expr.dom, 31),
        ("month", expr.month, 12),
        ("dow", expr.dow, 7),
    ]
    scores = {name: _field_equilibrium(val, total) for name, val, total in fields}
    overall = round(sum(scores.values()) / len(scores), 4)
    return EquilibriumResult(
        expression=expression,
        score=overall,
        grade=_grade(overall),
        scores=scores,
    )


def batch_equilibrium(expressions: list) -> list:
    return [assess_equilibrium(e) for e in expressions]
