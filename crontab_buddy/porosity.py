"""Porosity: measures how 'open' a cron expression is — how many time slots it leaves unfilled."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError

_FIELD_RANGES = [
    ("minute", 60),
    ("hour", 24),
    ("dom", 31),
    ("month", 12),
    ("dow", 7),
]


def _grade(score: float) -> str:
    if score >= 0.90:
        return "porous"
    if score >= 0.70:
        return "open"
    if score >= 0.45:
        return "semi-open"
    if score >= 0.20:
        return "dense"
    return "sealed"


def _field_porosity(value: str, slots: int) -> float:
    """Return fraction of slots NOT covered (1.0 = fully porous, 0.0 = sealed)."""
    if value == "*":
        return 1.0
    if "," in value:
        parts = value.split(",")
        return max(0.0, 1.0 - len(parts) / slots)
    if "-" in value and "/" not in value:
        lo, hi = value.split("-", 1)
        try:
            covered = int(hi) - int(lo) + 1
            return max(0.0, 1.0 - covered / slots)
        except ValueError:
            return 0.5
    if value.startswith("*/"):
        try:
            step = int(value[2:])
            covered = slots // max(1, step)
            return max(0.0, 1.0 - covered / slots)
        except ValueError:
            return 0.5
    return 0.0  # exact value


@dataclass
class PorosityResult:
    expression: str
    score: float
    grade: str
    scores: dict = field(default_factory=dict)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"Porosity({self.expression!r}): error — {self.error}"
        return f"Porosity({self.expression!r}): {self.grade} ({self.score:.3f})"


def assess_porosity(expression: str) -> PorosityResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return PorosityResult(expression=expression, score=0.0, grade="sealed", error=str(exc))

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    per_field: dict[str, float] = {}
    for (name, slots), val in zip(_FIELD_RANGES, fields):
        per_field[name] = _field_porosity(val, slots)

    overall = sum(per_field.values()) / len(per_field)
    return PorosityResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores=per_field,
    )


def batch_porosity(expressions: list[str]) -> list[PorosityResult]:
    return [assess_porosity(e) for e in expressions]
