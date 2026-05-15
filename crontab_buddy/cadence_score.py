"""Cadence scoring — combines multiple signal modules into a unified score."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds
from crontab_buddy.complexity import score_expression as complexity_score
from crontab_buddy.entropy import compute_entropy
from crontab_buddy.regularity import assess_regularity


_GRADE_THRESHOLDS = [
    (0.85, "A"),
    (0.70, "B"),
    (0.55, "C"),
    (0.40, "D"),
    (0.00, "F"),
]


@dataclass
class CadenceScoreResult:
    expression: str
    score: float
    grade: str
    interval_seconds: Optional[int]
    complexity_level: str
    entropy_level: str
    regularity_grade: str
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"CadenceScore({self.expression!r}) -> ERROR: {self.error}"
        return (
            f"CadenceScore({self.expression!r}) "
            f"score={self.score:.2f} grade={self.grade}"
        )


def _grade(score: float) -> str:
    for threshold, label in _GRADE_THRESHOLDS:
        if score >= threshold:
            return label
    return "F"


def compute_cadence_score(expression: str) -> CadenceScoreResult:
    """Compute a unified cadence score from multiple signal modules."""
    try:
        CronExpression(expression)
    except CronParseError as exc:
        return CadenceScoreResult(
            expression=expression,
            score=0.0,
            grade="F",
            interval_seconds=None,
            complexity_level="unknown",
            entropy_level="unknown",
            regularity_grade="F",
            error=str(exc),
        )

    interval = recurrence_interval_seconds(expression)
    cx = complexity_score(expression)
    ent = compute_entropy(expression)
    reg = assess_regularity(expression)

    # Normalise interval: shorter = lower score contribution (busier = riskier)
    if interval and interval > 0:
        interval_score = min(1.0, interval / 86400)
    else:
        interval_score = 0.0

    complexity_norm = max(0.0, 1.0 - cx.score / 20.0)
    entropy_norm = max(0.0, 1.0 - ent.score)
    regularity_norm = reg.score

    score = round(
        0.30 * interval_score
        + 0.20 * complexity_norm
        + 0.25 * entropy_norm
        + 0.25 * regularity_norm,
        4,
    )

    return CadenceScoreResult(
        expression=expression,
        score=score,
        grade=_grade(score),
        interval_seconds=interval,
        complexity_level=str(cx.label),
        entropy_level=str(ent.label),
        regularity_grade=reg.grade,
    )
