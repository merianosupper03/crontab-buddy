"""Elasticity: measures how adaptable/flexible a cron expression is across time ranges."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "supple"
    if score >= 0.65:
        return "flexible"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "stiff"
    return "rigid"


def _field_elasticity(field_str: str, max_val: int) -> float:
    """Score 0-1: how elastic (wide-ranging) a single field is."""
    if field_str == "*":
        return 1.0
    if "," in field_str:
        parts = field_str.split(",")
        return min(1.0, len(parts) / max(max_val, 1))
    if "-" in field_str:
        lo, hi = field_str.split("-", 1)
        try:
            span = int(hi) - int(lo) + 1
            return min(1.0, span / max(max_val, 1))
        except ValueError:
            return 0.1
    if field_str.startswith("*/"):
        try:
            step = int(field_str[2:])
            return min(1.0, (max_val / max(step, 1)) / max_val)
        except ValueError:
            return 0.1
    return 0.05


@dataclass
class ElasticityResult:
    expression: str
    score: float
    grade: str
    scores: dict
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"ElasticityResult(error={self.error})"
        return f"ElasticityResult(expression={self.expression!r}, grade={self.grade}, score={self.score:.3f})"


def assess_elasticity(expression: str) -> ElasticityResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ElasticityResult(expression=expression, score=0.0, grade="rigid", scores={}, error=str(exc))

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    maxes = [59, 23, 31, 12, 7]
    names = ["minute", "hour", "dom", "month", "dow"]

    scores = {name: _field_elasticity(f, mx) for name, f, mx in zip(names, fields, maxes)}
    overall = sum(scores.values()) / len(scores)
    return ElasticityResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores={k: round(v, 4) for k, v in scores.items()},
    )


def batch_elasticity(expressions: list[str]) -> list[ElasticityResult]:
    return [assess_elasticity(e) for e in expressions]
