"""Freshness scoring for cron expressions based on recent run activity."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

STALENESS_THRESHOLDS = {
    "fresh": 1,      # ran within 1 day
    "recent": 7,     # ran within 7 days
    "aging": 30,     # ran within 30 days
    "stale": 90,     # ran within 90 days
    # beyond 90 days -> "expired"
}


@dataclass
class FreshnessResult:
    expression: str
    last_seen: Optional[datetime]
    days_since: Optional[float]
    label: str
    score: float  # 0.0 (expired) to 1.0 (fresh)

    def __str__(self) -> str:
        if self.last_seen is None:
            return f"{self.expression} — never seen (score: 0.00)"
        return (
            f"{self.expression} — {self.label} "
            f"({self.days_since:.1f}d ago, score: {self.score:.2f})"
        )


def _label_and_score(days: float) -> tuple:
    if days <= STALENESS_THRESHOLDS["fresh"]:
        return "fresh", 1.0
    if days <= STALENESS_THRESHOLDS["recent"]:
        return "recent", 0.75
    if days <= STALENESS_THRESHOLDS["aging"]:
        return "aging", 0.50
    if days <= STALENESS_THRESHOLDS["stale"]:
        return "stale", 0.25
    return "expired", 0.0


def assess_freshness(
    expression: str,
    last_seen: Optional[datetime] = None,
) -> FreshnessResult:
    """Assess how fresh an expression is based on when it was last seen."""
    if last_seen is None:
        return FreshnessResult(
            expression=expression,
            last_seen=None,
            days_since=None,
            label="unknown",
            score=0.0,
        )

    now = datetime.now(timezone.utc)
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)

    delta = now - last_seen
    days = delta.total_seconds() / 86400.0
    label, score = _label_and_score(days)

    return FreshnessResult(
        expression=expression,
        last_seen=last_seen,
        days_since=round(days, 2),
        label=label,
        score=score,
    )


def batch_freshness(entries: list) -> list:
    """Assess freshness for a list of (expression, last_seen) tuples."""
    return [assess_freshness(expr, ts) for expr, ts in entries]
