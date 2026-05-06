"""Velocity: measure how frequently a cron expression has been used recently."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from crontab_buddy.history import get_history


_WINDOWS = {
    "1h": 3600,
    "24h": 86400,
    "7d": 604800,
    "30d": 2592000,
}


@dataclass
class VelocityResult:
    expression: str
    window: str
    count: int
    rate_per_hour: float
    level: str

    def __str__(self) -> str:
        return (
            f"{self.expression} | window={self.window} "
            f"count={self.count} rate={self.rate_per_hour:.2f}/hr level={self.level}"
        )


def _level(rate: float) -> str:
    if rate >= 10:
        return "high"
    if rate >= 1:
        return "moderate"
    if rate > 0:
        return "low"
    return "idle"


def compute_velocity(expression: str, window: str = "24h") -> VelocityResult:
    """Count how many times *expression* appears in history within *window*."""
    seconds = _WINDOWS.get(window)
    if seconds is None:
        raise ValueError(f"Unknown window '{window}'. Choose from: {list(_WINDOWS)}.")

    now = datetime.now(tz=timezone.utc).timestamp()
    cutoff = now - seconds

    count = sum(
        1
        for entry in get_history()
        if entry.get("expression") == expression
        and entry.get("timestamp", 0) >= cutoff
    )

    hours = seconds / 3600
    rate = count / hours
    return VelocityResult(
        expression=expression,
        window=window,
        count=count,
        rate_per_hour=rate,
        level=_level(rate),
    )


def batch_velocity(expressions: List[str], window: str = "24h") -> List[VelocityResult]:
    return [compute_velocity(expr, window) for expr in expressions]
