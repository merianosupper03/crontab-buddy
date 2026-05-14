"""Luminosity: measures how 'bright' or prominent a cron expression is
based on how often it fires during peak hours (8am-6pm) vs off-peak."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError

PEAK_HOURS = set(range(8, 18))  # 8am to 5:59pm


def _grade(score: float) -> str:
    if score >= 0.85:
        return "radiant"
    if score >= 0.65:
        return "bright"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "dim"
    return "dark"


def _peak_firing_ratio(expr: CronExpression) -> float:
    """Return fraction of firing minutes that fall in peak hours."""
    hour_field = expr.fields[1]
    if hour_field == "*":
        hours = list(range(24))
    elif "/" in hour_field and hour_field.startswith("*/"):
        step = int(hour_field.split("/")[1])
        hours = list(range(0, 24, step))
    elif "-" in hour_field:
        lo, hi = hour_field.split("-")
        hours = list(range(int(lo), int(hi) + 1))
    elif "," in hour_field:
        hours = [int(h) for h in hour_field.split(",")]
    else:
        try:
            hours = [int(hour_field)]
        except ValueError:
            hours = list(range(24))

    if not hours:
        return 0.0
    peak = sum(1 for h in hours if h in PEAK_HOURS)
    return peak / len(hours)


@dataclass
class LuminosityResult:
    expression: str
    score: float
    grade: str
    peak_ratio: float
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"LuminosityResult(error={self.error})"
        return (
            f"LuminosityResult(expression={self.expression!r}, "
            f"grade={self.grade}, score={self.score:.2f}, "
            f"peak_ratio={self.peak_ratio:.2f})"
        )


def assess_luminosity(expression: str) -> LuminosityResult:
    """Assess how luminous (peak-hour-focused) a cron expression is."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return LuminosityResult(
            expression=expression,
            score=0.0,
            grade="dark",
            peak_ratio=0.0,
            error=str(exc),
        )
    ratio = _peak_firing_ratio(expr)
    grade = _grade(ratio)
    return LuminosityResult(
        expression=expression,
        score=round(ratio, 4),
        grade=grade,
        peak_ratio=round(ratio, 4),
    )


def batch_luminosity(expressions: list[str]) -> list[LuminosityResult]:
    return [assess_luminosity(e) for e in expressions]
