"""Turbulence: measure how erratic a cron expression's firing pattern is."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class TurbulenceResult:
    expression: str
    score: float  # 0.0 = smooth, 1.0 = maximally turbulent
    label: str
    intervals: List[int] = field(default_factory=list)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"TurbulenceResult({self.expression!r}, error={self.error!r})"
        return (
            f"TurbulenceResult({self.expression!r}, "
            f"score={self.score:.3f}, label={self.label!r})"
        )


def _grade(score: float) -> str:
    if score < 0.15:
        return "smooth"
    if score < 0.35:
        return "gentle"
    if score < 0.55:
        return "moderate"
    if score < 0.75:
        return "rough"
    return "turbulent"


def _firing_minutes_per_hour(expr: CronExpression) -> List[int]:
    """Return the list of minute-of-hour values this expression fires on."""
    minute_field = expr.fields[0]
    results: List[int] = []

    if minute_field == "*":
        return list(range(60))

    for part in minute_field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            results.extend(range(start, 60, int(step)))
        elif "-" in part:
            lo, hi = part.split("-", 1)
            results.extend(range(int(lo), int(hi) + 1))
        else:
            results.append(int(part))

    return sorted(set(results))


def assess_turbulence(expression: str) -> TurbulenceResult:
    """Assess how turbulent (erratic) a cron expression's firing pattern is."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return TurbulenceResult(
            expression=expression,
            score=0.0,
            label="unknown",
            error=str(exc),
        )

    minutes = _firing_minutes_per_hour(expr)

    if len(minutes) <= 1:
        return TurbulenceResult(
            expression=expression,
            score=1.0,
            label="turbulent",
            intervals=[],
        )

    intervals = [minutes[i + 1] - minutes[i] for i in range(len(minutes) - 1)]
    mean = sum(intervals) / len(intervals)
    variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
    # normalise: max possible std-dev for minutes 0-59 is ~30
    std_dev = variance ** 0.5
    score = min(1.0, std_dev / 30.0)

    return TurbulenceResult(
        expression=expression,
        score=round(score, 4),
        label=_grade(score),
        intervals=intervals,
    )


def batch_turbulence(expressions: List[str]) -> List[TurbulenceResult]:
    return [assess_turbulence(e) for e in expressions]
