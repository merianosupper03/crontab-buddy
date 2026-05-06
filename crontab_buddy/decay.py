"""Decay scoring for cron expressions based on last-used recency."""

import math
from datetime import datetime, timezone
from typing import Optional


_DECAY_HALF_LIVES = {
    "fast": 7,    # 7 days
    "normal": 30, # 30 days
    "slow": 90,   # 90 days
}


class DecayResult:
    def __init__(self, expression: str, score: float, age_days: float, half_life: str):
        self.expression = expression
        self.score = round(score, 4)
        self.age_days = round(age_days, 2)
        self.half_life = half_life

    def __str__(self) -> str:
        return (
            f"Expression : {self.expression}\n"
            f"Age (days) : {self.age_days}\n"
            f"Half-life  : {self.half_life} ({_DECAY_HALF_LIVES[self.half_life]} days)\n"
            f"Decay score: {self.score} (1.0 = fresh, 0.0 = stale)"
        )


def compute_decay(
    expression: str,
    last_used: datetime,
    half_life: str = "normal",
    now: Optional[datetime] = None,
) -> DecayResult:
    """Compute an exponential decay score for an expression.

    Score of 1.0 means just used; approaches 0.0 as time passes.
    """
    if half_life not in _DECAY_HALF_LIVES:
        raise ValueError(
            f"Unknown half_life '{half_life}'. Choose from: {list(_DECAY_HALF_LIVES)}"
        )

    if now is None:
        now = datetime.now(timezone.utc)

    # Ensure both are offset-aware for subtraction
    if last_used.tzinfo is None:
        last_used = last_used.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    age_days = max((now - last_used).total_seconds() / 86400, 0.0)
    hl = _DECAY_HALF_LIVES[half_life]
    score = math.pow(0.5, age_days / hl)
    return DecayResult(expression=expression, score=score, age_days=age_days, half_life=half_life)


def is_stale(result: DecayResult, threshold: float = 0.1) -> bool:
    """Return True if the decay score is below the given threshold."""
    return result.score < threshold


def format_decay(result: DecayResult) -> str:
    return str(result)
