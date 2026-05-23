"""Wavelength: measures the characteristic period between cron firings."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.scheduler import next_runs
from datetime import datetime, timezone

_GRADES = [
    (0.0, "instantaneous"),
    (0.1, "ultra-short"),
    (0.3, "short"),
    (0.5, "medium"),
    (0.75, "long"),
    (1.0, "extended"),
]


def _grade(score: float) -> str:
    for threshold, label in _GRADES:
        if score <= threshold:
            return label
    return "extended"


@dataclass
class WavelengthResult:
    expression: str
    period_seconds: float
    score: float
    label: str
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"WavelengthResult(expression={self.expression!r}, error={self.error!r})"
        return (
            f"WavelengthResult(expression={self.expression!r}, "
            f"period_seconds={self.period_seconds:.1f}, label={self.label!r})"
        )


def assess_wavelength(expression: str) -> WavelengthResult:
    """Compute the wavelength (inter-firing period) of a cron expression."""
    try:
        CronExpression(expression)
    except CronParseError as exc:
        return WavelengthResult(
            expression=expression,
            period_seconds=0.0,
            score=0.0,
            label="unknown",
            error=str(exc),
        )

    anchor = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    runs = next_runs(expression, anchor, count=2)
    if len(runs) < 2:
        return WavelengthResult(
            expression=expression,
            period_seconds=0.0,
            score=0.0,
            label="unknown",
            error="Could not compute two consecutive runs",
        )

    period = (runs[1] - runs[0]).total_seconds()
    # Normalise: 60s -> ~0, 604800s (weekly) -> ~1
    max_period = 604800.0
    score = min(period / max_period, 1.0)
    return WavelengthResult(
        expression=expression,
        period_seconds=period,
        score=round(score, 4),
        label=_grade(score),
    )


def batch_wavelength(expressions: List[str]) -> List[WavelengthResult]:
    return [assess_wavelength(e) for e in expressions]
