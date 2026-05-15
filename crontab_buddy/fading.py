"""Fading: measures how quickly a cron expression's relevance diminishes over time."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.recurrence import recurrence_interval_seconds


INTERVAL_THRESHOLDS = [
    (60,       1.0,  "instant"),
    (3600,     0.85, "rapid"),
    (86400,    0.65, "moderate"),
    (604800,   0.40, "gradual"),
    (2592000,  0.20, "slow"),
    (float("inf"), 0.05, "glacial"),
]


def _grade(score: float) -> str:
    if score >= 0.9:
        return "A"
    if score >= 0.75:
        return "B"
    if score >= 0.55:
        return "C"
    if score >= 0.35:
        return "D"
    return "F"


@dataclass
class FadingResult:
    expression: str
    score: float
    label: str
    grade: str
    interval_seconds: Optional[float]
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"FadingResult({self.expression!r}, error={self.error!r})"
        return (
            f"FadingResult({self.expression!r}, score={self.score:.3f}, "
            f"label={self.label!r}, grade={self.grade!r})"
        )


def assess_fading(expression: str) -> FadingResult:
    """Assess how quickly the expression's relevance fades (inverse of frequency)."""
    try:
        interval = recurrence_interval_seconds(expression)
    except Exception as exc:
        return FadingResult(
            expression=expression,
            score=0.0,
            label="unknown",
            grade="F",
            interval_seconds=None,
            error=str(exc),
        )

    for threshold, score, label in INTERVAL_THRESHOLDS:
        if interval <= threshold:
            return FadingResult(
                expression=expression,
                score=score,
                label=label,
                grade=_grade(score),
                interval_seconds=interval,
            )

    return FadingResult(
        expression=expression,
        score=0.05,
        label="glacial",
        grade="F",
        interval_seconds=interval,
    )


def batch_fading(expressions: list[str]) -> list[FadingResult]:
    return [assess_fading(expr) for expr in expressions]
