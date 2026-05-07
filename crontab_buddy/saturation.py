"""Saturation: measure how fully a cron expression utilises each time field."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError

FIELD_RANGES = {
    "minute": 60,
    "hour": 24,
    "dom": 31,
    "month": 12,
    "dow": 7,
}


@dataclass
class SaturationResult:
    expression: str
    scores: dict  # field -> float 0-1
    overall: float
    grade: str
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"SaturationResult(error={self.error})"
        parts = ", ".join(f"{k}={v:.2f}" for k, v in self.scores.items())
        return f"SaturationResult({parts}, overall={self.overall:.2f}, grade={self.grade})"


def _grade(score: float) -> str:
    if score >= 0.8:
        return "saturated"
    if score >= 0.5:
        return "moderate"
    if score >= 0.2:
        return "sparse"
    return "minimal"


def _field_saturation(field_value: str, total: int) -> float:
    """Estimate what fraction of possible values a field covers."""
    if field_value == "*":
        return 1.0
    if "," in field_value:
        parts = field_value.split(",")
        return min(len(parts) / total, 1.0)
    if "-" in field_value and "/" not in field_value:
        lo, hi = field_value.split("-", 1)
        try:
            span = int(hi) - int(lo) + 1
            return min(span / total, 1.0)
        except ValueError:
            return 0.1
    if field_value.startswith("*/"):
        try:
            step = int(field_value[2:])
            return min(1.0 / step, 1.0) if step > 0 else 1.0
        except ValueError:
            return 0.1
    if "/" in field_value:
        return 0.3
    return 1.0 / total


def assess_saturation(expression: str) -> SaturationResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return SaturationResult(
            expression=expression,
            scores={},
            overall=0.0,
            grade="minimal",
            error=str(exc),
        )
    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = list(FIELD_RANGES.keys())
    totals = list(FIELD_RANGES.values())
    scores = {name: _field_saturation(val, tot) for name, val, tot in zip(names, fields, totals)}
    overall = sum(scores.values()) / len(scores)
    return SaturationResult(
        expression=expression,
        scores=scores,
        overall=round(overall, 4),
        grade=_grade(overall),
    )
