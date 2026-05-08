"""Isolation scoring for cron expressions.

Measures how isolated (unique in time) a cron expression is relative to
others — higher isolation means fewer temporal neighbours.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.scheduler import next_runs


@dataclass
class IsolationResult:
    expression: str
    score: float  # 0.0 – 1.0
    grade: str
    neighbours: int
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"IsolationResult({self.expression!r}, error={self.error!r})"
        return (
            f"IsolationResult({self.expression!r}, score={self.score:.2f}, "
            f"grade={self.grade!r}, neighbours={self.neighbours})"
        )


def _grade(score: float) -> str:
    if score >= 0.85:
        return "isolated"
    if score >= 0.60:
        return "sparse"
    if score >= 0.35:
        return "moderate"
    return "crowded"


def _firing_minutes(expr: CronExpression, horizon_hours: int = 24) -> List[int]:
    """Return list of minutes-since-epoch-start within the horizon."""
    from datetime import datetime
    base = datetime(2024, 1, 1, 0, 0)
    runs = next_runs(expr, base, count=horizon_hours * 60)
    result = []
    for r in runs:
        delta = int((r - base).total_seconds() // 60)
        if delta < horizon_hours * 60:
            result.append(delta)
    return result


def assess_isolation(
    expression: str,
    peers: Optional[List[str]] = None,
    horizon_hours: int = 24,
) -> IsolationResult:
    """Assess how isolated *expression* is from *peers* over *horizon_hours*."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return IsolationResult(expression, 0.0, "crowded", 0, error=str(exc))

    my_minutes = set(_firing_minutes(expr, horizon_hours))
    if not my_minutes:
        return IsolationResult(expression, 1.0, "isolated", 0)

    overlap_count = 0
    for peer_expr_str in (peers or []):
        if peer_expr_str == expression:
            continue
        try:
            peer = CronExpression(peer_expr_str)
        except CronParseError:
            continue
        peer_minutes = set(_firing_minutes(peer, horizon_hours))
        overlap_count += len(my_minutes & peer_minutes)

    neighbours = min(overlap_count, len(my_minutes))
    score = max(0.0, 1.0 - neighbours / len(my_minutes))
    return IsolationResult(expression, round(score, 4), _grade(score), neighbours)
