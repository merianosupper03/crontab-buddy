"""Recency scoring for cron expressions based on last-seen timestamps."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional


RECENCY_THRESHOLDS = [
    (1,    "just now",   1.0),
    (60,   "very recent", 0.9),
    (1440, "recent",     0.7),
    (10080, "aging",     0.4),
    (43200, "old",       0.2),
]


class RecencyResult:
    def __init__(self, expression: str, last_seen: Optional[datetime],
                 score: float, label: str, minutes_ago: Optional[float]):
        self.expression = expression
        self.last_seen = last_seen
        self.score = score
        self.label = label
        self.minutes_ago = minutes_ago
        self.error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"RecencyResult(error={self.error})"
        return (
            f"RecencyResult(expression={self.expression!r}, "
            f"label={self.label!r}, score={self.score:.3f}, "
            f"minutes_ago={self.minutes_ago})"
        )


def _label_and_score(minutes_ago: float) -> tuple[str, float]:
    for threshold, label, score in RECENCY_THRESHOLDS:
        if minutes_ago <= threshold:
            return label, score
    return "ancient", 0.05


def assess_recency(
    expression: str,
    last_seen: Optional[datetime] = None,
) -> RecencyResult:
    """Score how recently an expression was last seen/used."""
    if last_seen is None:
        result = RecencyResult(expression, None, 0.0, "never seen", None)
        return result

    now = datetime.now(timezone.utc)
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)

    delta_minutes = (now - last_seen).total_seconds() / 60.0
    if delta_minutes < 0:
        delta_minutes = 0.0

    label, score = _label_and_score(delta_minutes)
    return RecencyResult(expression, last_seen, score, label, round(delta_minutes, 2))


def batch_recency(
    entries: list[tuple[str, Optional[datetime]]],
) -> list[RecencyResult]:
    """Assess recency for multiple (expression, last_seen) pairs."""
    return [assess_recency(expr, ts) for expr, ts in entries]
