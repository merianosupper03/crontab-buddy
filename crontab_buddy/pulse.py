"""Pulse: measure the 'heartbeat rate' of a cron expression as a normalized score."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds

_LEVELS = [
    (60,       "racing"),
    (300,      "rapid"),
    (3600,     "steady"),
    (21600,    "calm"),
    (86400,    "quiet"),
    (604800,   "dormant"),
]


def _level(interval_seconds: float) -> str:
    for threshold, label in _LEVELS:
        if interval_seconds <= threshold:
            return label
    return "dormant"


@dataclass
class PulseResult:
    expression: str
    interval_seconds: Optional[float]
    score: float  # 0.0 (slowest) .. 1.0 (fastest)
    level: str
    error: Optional[str] = field(default=None)

    def __str__(self) -> str:
        if self.error:
            return f"PulseResult(error={self.error})"
        return (
            f"PulseResult(expr={self.expression!r}, "
            f"level={self.level}, score={self.score:.3f})"
        )


def assess_pulse(expression: str) -> PulseResult:
    """Return a PulseResult describing how frequently the expression fires."""
    try:
        CronExpression(expression)
    except CronParseError as exc:
        return PulseResult(
            expression=expression,
            interval_seconds=None,
            score=0.0,
            level="unknown",
            error=str(exc),
        )

    interval = recurrence_interval_seconds(expression)
    if interval is None or interval <= 0:
        return PulseResult(
            expression=expression,
            interval_seconds=None,
            score=0.0,
            level="unknown",
            error="Could not determine recurrence interval",
        )

    # Score: fastest possible is every minute (60s) -> 1.0
    # Slowest meaningful cap is weekly (604800s) -> 0.0
    min_i, max_i = 60.0, 604800.0
    clamped = max(min_i, min(max_i, interval))
    score = 1.0 - (clamped - min_i) / (max_i - min_i)

    return PulseResult(
        expression=expression,
        interval_seconds=interval,
        score=round(score, 4),
        level=_level(interval),
    )


def batch_pulse(expressions: list[str]) -> list[PulseResult]:
    return [assess_pulse(e) for e in expressions]
