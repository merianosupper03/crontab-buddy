"""Bandwidth: estimate the data/event throughput footprint of cron expressions."""

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds


_GRADES = [
    (0.2,  "minimal"),
    (0.4,  "light"),
    (0.6,  "moderate"),
    (0.8,  "heavy"),
    (1.01, "saturated"),
]


def _grade(score: float) -> str:
    for threshold, label in _GRADES:
        if score < threshold:
            return label
    return "saturated"


@dataclass
class BandwidthResult:
    expression: str
    runs_per_hour: float
    runs_per_day: float
    score: float          # 0.0 (very low) .. 1.0 (very high)
    grade: str
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"BandwidthResult(error={self.error})"
        return (
            f"BandwidthResult(expression={self.expression!r}, "
            f"runs_per_day={self.runs_per_day:.1f}, "
            f"grade={self.grade})"
        )


def assess_bandwidth(expression: str) -> BandwidthResult:
    """Assess the bandwidth (firing rate) of a single cron expression."""
    try:
        CronExpression(expression)
    except CronParseError as exc:
        return BandwidthResult(
            expression=expression,
            runs_per_hour=0.0,
            runs_per_day=0.0,
            score=0.0,
            grade="minimal",
            error=str(exc),
        )

    interval = recurrence_interval_seconds(expression)
    if interval <= 0:
        interval = 86400  # fallback: once a day

    runs_per_hour = 3600 / interval
    runs_per_day = 86400 / interval

    # score: 1 run/min = 60/hr => score ~1.0; normalise against 60
    raw = runs_per_hour / 60.0
    score = min(raw, 1.0)

    return BandwidthResult(
        expression=expression,
        runs_per_hour=round(runs_per_hour, 4),
        runs_per_day=round(runs_per_day, 4),
        score=round(score, 4),
        grade=_grade(score),
    )


def batch_bandwidth(expressions: List[str]) -> List[BandwidthResult]:
    """Assess bandwidth for multiple expressions."""
    return [assess_bandwidth(e) for e in expressions]
