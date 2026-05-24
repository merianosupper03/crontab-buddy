"""Churn analysis: measures how frequently a cron expression's schedule changes
relative to a reference set of expressions (e.g. history or favorites)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.8:
        return "turbulent"
    if score >= 0.6:
        return "volatile"
    if score >= 0.4:
        return "shifting"
    if score >= 0.2:
        return "drifting"
    return "stable"


@dataclass
class ChurnResult:
    expression: str
    score: float
    grade: str
    unique_peers: int
    overlapping_peers: int
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"ChurnResult(error={self.error})"
        return (
            f"ChurnResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade}, "
            f"unique_peers={self.unique_peers}, overlapping_peers={self.overlapping_peers})"
        )


def _safe_parse(expr: str) -> Optional[CronExpression]:
    try:
        return CronExpression(expr)
    except (CronParseError, ValueError):
        return None


def _firing_minutes(expr: CronExpression) -> set:
    """Return set of (hour, minute) tuples that fire in a 24-hour window."""
    minutes_field = expr.fields[0]
    hours_field = expr.fields[1]

    def expand(field_val, max_val):
        if field_val == "*":
            return list(range(max_val))
        if "/" in field_val:
            base, step = field_val.split("/")
            start = 0 if base == "*" else int(base)
            return list(range(start, max_val, int(step)))
        if "-" in field_val:
            lo, hi = field_val.split("-")
            return list(range(int(lo), int(hi) + 1))
        if "," in field_val:
            return [int(v) for v in field_val.split(",")]
        return [int(field_val)]

    mins = expand(minutes_field, 60)
    hrs = expand(hours_field, 24)
    return {(h, m) for h in hrs for m in mins}


def assess_churn(expression: str, peers: List[str]) -> ChurnResult:
    """Assess churn of *expression* against a list of peer expressions."""
    parsed = _safe_parse(expression)
    if parsed is None:
        return ChurnResult(
            expression=expression,
            score=0.0,
            grade="stable",
            unique_peers=0,
            overlapping_peers=0,
            error=f"Invalid expression: {expression!r}",
        )

    own_minutes = _firing_minutes(parsed)
    unique_peers = 0
    overlapping_peers = 0

    seen_peer_minutes = set()
    for peer_expr in peers:
        if peer_expr.strip() == expression.strip():
            continue
        pp = _safe_parse(peer_expr)
        if pp is None:
            continue
        pm = _firing_minutes(pp)
        key = frozenset(pm)
        if key in seen_peer_minutes:
            continue
        seen_peer_minutes.add(key)
        unique_peers += 1
        if own_minutes & pm:
            overlapping_peers += 1

    if unique_peers == 0:
        score = 0.0
    else:
        score = round(overlapping_peers / unique_peers, 4)

    return ChurnResult(
        expression=expression,
        score=score,
        grade=_grade(score),
        unique_peers=unique_peers,
        overlapping_peers=overlapping_peers,
    )


def batch_churn(expressions: List[str]) -> List[ChurnResult]:
    """Assess churn for each expression using all others as peers."""
    results = []
    for expr in expressions:
        peers = [e for e in expressions if e != expr]
        results.append(assess_churn(expr, peers))
    return results
