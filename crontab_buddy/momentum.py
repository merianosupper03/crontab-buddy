"""Momentum: measures how consistently an expression has been used over time."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from crontab_buddy.history import get_history


@dataclass
class MomentumResult:
    expression: str
    total_uses: int
    recent_uses: int  # last 7 days
    score: float  # 0.0 - 1.0
    level: str

    def __str__(self) -> str:
        return (
            f"Expression : {self.expression}\n"
            f"Total uses : {self.total_uses}\n"
            f"Recent uses: {self.recent_uses} (last 7 days)\n"
            f"Score      : {self.score:.2f}\n"
            f"Momentum   : {self.level}"
        )


def _level(score: float) -> str:
    if score >= 0.8:
        return "surging"
    if score >= 0.6:
        return "strong"
    if score >= 0.4:
        return "steady"
    if score >= 0.2:
        return "fading"
    return "idle"


def compute_momentum(expression: str, history_path: str | None = None) -> MomentumResult:
    """Compute momentum for an expression based on usage history."""
    kwargs = {"path": history_path} if history_path else {}
    entries = get_history(**kwargs)

    from datetime import datetime, timezone, timedelta

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    total_uses = 0
    recent_uses = 0

    for entry in entries:
        if entry.get("expression") != expression:
            continue
        total_uses += 1
        ts_raw = entry.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_raw)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff:
                recent_uses += 1
        except (ValueError, TypeError):
            pass

    if total_uses == 0:
        score = 0.0
    else:
        recency_ratio = recent_uses / max(total_uses, 1)
        volume_factor = min(total_uses / 20.0, 1.0)
        score = round(0.6 * recency_ratio + 0.4 * volume_factor, 4)

    return MomentumResult(
        expression=expression,
        total_uses=total_uses,
        recent_uses=recent_uses,
        score=score,
        level=_level(score),
    )


def batch_momentum(expressions: List[str], history_path: str | None = None) -> List[MomentumResult]:
    """Compute momentum for multiple expressions, sorted by score descending."""
    results = [compute_momentum(expr, history_path=history_path) for expr in expressions]
    return sorted(results, key=lambda r: r.score, reverse=True)
