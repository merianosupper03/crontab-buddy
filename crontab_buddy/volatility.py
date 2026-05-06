"""Volatility analysis for cron expressions.

Measures how often an expression fires relative to its complexity,
giving a sense of how 'volatile' or unpredictable the schedule is.
"""

from dataclasses import dataclass
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds


VOLATILITY_THRESHOLDS = [
    (60, "extreme"),       # fires every minute
    (300, "very_high"),    # fires every 5 minutes
    (3600, "high"),        # fires every hour
    (21600, "moderate"),   # fires every 6 hours
    (86400, "low"),        # fires daily
    (604800, "very_low"),  # fires weekly
]


@dataclass
class VolatilityResult:
    expression: str
    interval_seconds: int
    level: str
    score: float  # 0.0 (stable) to 1.0 (extremely volatile)
    description: str
    valid: bool
    error: str = ""

    def __str__(self) -> str:
        if not self.valid:
            return f"VolatilityResult(invalid: {self.error})"
        return (
            f"VolatilityResult(expression={self.expression!r}, "
            f"level={self.level}, score={self.score:.2f})"
        )


def _level_and_score(interval_seconds: int) -> tuple:
    for threshold, level in VOLATILITY_THRESHOLDS:
        if interval_seconds <= threshold:
            score = max(0.0, 1.0 - (interval_seconds / 604800))
            return level, round(score, 4)
    return "stable", 0.0


def assess_volatility(expression: str) -> VolatilityResult:
    """Assess the volatility of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return VolatilityResult(
            expression=expression,
            interval_seconds=0,
            level="unknown",
            score=0.0,
            description="Invalid expression.",
            valid=False,
            error=str(exc),
        )

    interval = recurrence_interval_seconds(str(expr))
    level, score = _level_and_score(interval)
    desc = f"Fires approximately every {interval}s ({level} volatility)."
    return VolatilityResult(
        expression=str(expr),
        interval_seconds=interval,
        level=level,
        score=score,
        description=desc,
        valid=True,
    )


def batch_volatility(expressions: list) -> list:
    """Assess volatility for a list of expressions."""
    return [assess_volatility(e) for e in expressions]
