"""Directionality: assess whether a cron expression skews toward
morning, afternoon, evening, or night firing patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


DAYTIME_BUCKETS = {
    "night": range(0, 6),
    "morning": range(6, 12),
    "afternoon": range(12, 18),
    "evening": range(18, 24),
}


def _grade(score: float) -> str:
    if score >= 0.85:
        return "dominant"
    if score >= 0.65:
        return "leaning"
    if score >= 0.40:
        return "mixed"
    return "neutral"


def _firing_hours(expr: CronExpression) -> list[int]:
    h = expr.hour
    if h == "*":
        return list(range(24))
    hours: list[int] = []
    for part in h.split(","):
        if "-" in part:
            a, b = part.split("-")
            hours.extend(range(int(a), int(b) + 1))
        elif "/" in part:
            base, step = part.split("/")
            start = 0 if base == "*" else int(base)
            hours.extend(range(start, 24, int(step)))
        else:
            hours.append(int(part))
    return hours


@dataclass
class DirectionalityResult:
    expression: str
    dominant_period: Optional[str]
    scores: dict[str, float]
    grade: str
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"Directionality({self.expression}): error={self.error}"
        return (
            f"Directionality({self.expression}): "
            f"dominant={self.dominant_period}, grade={self.grade}"
        )


def assess_directionality(expression: str) -> DirectionalityResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return DirectionalityResult(
            expression=expression,
            dominant_period=None,
            scores={},
            grade="neutral",
            error=str(exc),
        )

    hours = _firing_hours(expr)
    total = len(hours) or 1
    bucket_counts: dict[str, int] = {k: 0 for k in DAYTIME_BUCKETS}
    for h in hours:
        for bucket, rng in DAYTIME_BUCKETS.items():
            if h in rng:
                bucket_counts[bucket] += 1

    scores = {k: round(v / total, 4) for k, v in bucket_counts.items()}
    dominant = max(scores, key=lambda k: scores[k])
    dominant_score = scores[dominant]
    grade = _grade(dominant_score)
    return DirectionalityResult(
        expression=expression,
        dominant_period=dominant,
        scores=scores,
        grade=grade,
    )


def batch_directionality(expressions: list[str]) -> list[DirectionalityResult]:
    return [assess_directionality(e) for e in expressions]
