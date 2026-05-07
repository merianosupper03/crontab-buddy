"""Dispersion analysis — measures how evenly a cron expression distributes
its firing times across a time window."""

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class DispersionResult:
    expression: str
    score: float  # 0.0 (clustered) to 1.0 (evenly spread)
    label: str
    intervals: List[int]  # minutes between consecutive fires in a 24h window
    mean_interval: float
    std_dev: float
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"DispersionResult({self.expression!r}, error={self.error!r})"
        return (
            f"DispersionResult({self.expression!r}, score={self.score:.3f},"
            f" label={self.label!r}, mean_interval={self.mean_interval:.1f}m)"
        )


def _grade(score: float) -> str:
    if score >= 0.85:
        return "uniform"
    if score >= 0.65:
        return "spread"
    if score >= 0.40:
        return "uneven"
    return "clustered"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return sorted list of minutes-of-day when expr fires within 24 hours."""
    from crontab_buddy.scheduler import _matches_field

    fires = []
    for h in range(24):
        for m in range(60):
            if _matches_field(str(expr.minute), m, 0, 59) and \
               _matches_field(str(expr.hour), h, 0, 23):
                fires.append(h * 60 + m)
    return fires


def assess_dispersion(expression: str) -> DispersionResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return DispersionResult(
            expression=expression, score=0.0, label="clustered",
            intervals=[], mean_interval=0.0, std_dev=0.0, error=str(exc)
        )

    fires = _firing_minutes(expr)
    if len(fires) < 2:
        return DispersionResult(
            expression=expression, score=0.0, label="clustered",
            intervals=[], mean_interval=0.0, std_dev=0.0
        )

    intervals = [fires[i + 1] - fires[i] for i in range(len(fires) - 1)]
    mean = sum(intervals) / len(intervals)
    variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
    std = variance ** 0.5

    # coefficient of variation, inverted and clamped to [0, 1]
    cv = (std / mean) if mean > 0 else 1.0
    score = max(0.0, min(1.0, 1.0 - cv))

    return DispersionResult(
        expression=expression,
        score=round(score, 4),
        label=_grade(score),
        intervals=intervals,
        mean_interval=round(mean, 2),
        std_dev=round(std, 2),
    )
