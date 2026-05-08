"""Tempo: assess the execution pace/rhythm of a cron expression."""
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds


TEMPO_LEVELS = ["glacial", "slow", "moderate", "brisk", "rapid", "frantic"]


@dataclass
class TempoResult:
    expression: str
    interval_seconds: Optional[int]
    level: str
    score: float  # 0.0 (slowest) to 1.0 (fastest)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"TempoResult(error={self.error})"
        return (
            f"TempoResult(expression={self.expression!r}, "
            f"level={self.level}, score={self.score:.3f}, "
            f"interval={self.interval_seconds}s)"
        )


def _level_and_score(interval_seconds: Optional[int]) -> tuple:
    """Map interval in seconds to a tempo level and score."""
    if interval_seconds is None:
        return "glacial", 0.0
    thresholds = [
        (60, "frantic", 1.0),
        (300, "rapid", 0.85),
        (3600, "brisk", 0.65),
        (21600, "moderate", 0.45),
        (86400, "slow", 0.25),
    ]
    for limit, label, score in thresholds:
        if interval_seconds <= limit:
            return label, score
    return "glacial", 0.05


def assess_tempo(expression: str) -> TempoResult:
    """Assess the tempo (pace) of a cron expression."""
    try:
        CronExpression(expression)
    except CronParseError as exc:
        return TempoResult(
            expression=expression,
            interval_seconds=None,
            level="glacial",
            score=0.0,
            error=str(exc),
        )
    interval = recurrence_interval_seconds(expression)
    level, score = _level_and_score(interval)
    return TempoResult(
        expression=expression,
        interval_seconds=interval,
        level=level,
        score=score,
    )


def batch_tempo(expressions: list) -> list:
    """Assess tempo for a list of expressions."""
    return [assess_tempo(expr) for expr in expressions]
