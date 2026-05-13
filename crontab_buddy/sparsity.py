"""Sparsity analysis: measures how infrequently a cron expression fires."""

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds


_GRADES = [
    (86400 * 30, "glacial"),
    (86400 * 7,  "sparse"),
    (86400,      "infrequent"),
    (3600,       "occasional"),
    (600,        "moderate"),
    (60,         "dense"),
    (0,          "saturated"),
]


def _grade(interval_seconds: float) -> str:
    for threshold, label in _GRADES:
        if interval_seconds >= threshold:
            return label
    return "saturated"


@dataclass
class SparsityResult:
    expression: str
    interval_seconds: float
    grade: str
    score: float  # 0.0 = fires constantly, 1.0 = fires very rarely
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"SparsityResult(error={self.error!r})"
        return (
            f"SparsityResult(expression={self.expression!r}, "
            f"grade={self.grade!r}, score={self.score:.3f})"
        )


def assess_sparsity(expression: str) -> SparsityResult:
    """Assess how sparse (infrequent) a cron expression is."""
    try:
        CronExpression(expression)
    except CronParseError as exc:
        return SparsityResult(
            expression=expression,
            interval_seconds=0.0,
            grade="unknown",
            score=0.0,
            error=str(exc),
        )

    interval = recurrence_interval_seconds(expression)
    # Normalise against one month (approx 2592000s) as the upper bound
    max_interval = 86400 * 30
    score = min(interval / max_interval, 1.0)
    return SparsityResult(
        expression=expression,
        interval_seconds=interval,
        grade=_grade(interval),
        score=round(score, 4),
    )


def batch_sparsity(expressions: List[str]) -> List[SparsityResult]:
    """Assess sparsity for a list of expressions."""
    return [assess_sparsity(e) for e in expressions]
