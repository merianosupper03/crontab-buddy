"""Contrast: measure how distinct a cron expression is from a reference set."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "vivid"
    if score >= 0.65:
        return "distinct"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "muted"
    return "indistinct"


def _firing_minutes(expr: CronExpression) -> set:
    """Return a set of (hour, minute) tuples the expression fires in a day."""
    minutes_field = expr.minute
    hours_field = expr.hour

    def expand(field_val: str, max_val: int) -> List[int]:
        if field_val == "*":
            return list(range(max_val))
        results = []
        for part in field_val.split(","):
            if "/" in part:
                base, step = part.split("/", 1)
                start = 0 if base == "*" else int(base.split("-")[0])
                results.extend(range(start, max_val, int(step)))
            elif "-" in part:
                a, b = part.split("-", 1)
                results.extend(range(int(a), int(b) + 1))
            else:
                results.append(int(part))
        return results

    mins = expand(minutes_field, 60)
    hrs = expand(hours_field, 24)
    return {(h, m) for h in hrs for m in mins}


@dataclass
class ContrastResult:
    expression: str
    score: float
    grade: str
    shared_minutes: int
    total_minutes: int
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"ContrastResult(error={self.error})"
        return (
            f"ContrastResult(expr={self.expression!r}, "
            f"grade={self.grade}, score={self.score:.3f}, "
            f"shared={self.shared_minutes}/{self.total_minutes})"
        )


def assess_contrast(expression: str, peers: List[str]) -> ContrastResult:
    """Assess how distinct *expression* is from the list of *peers*.

    A high score means the expression fires at times not covered by peers.
    """
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ContrastResult(
            expression=expression,
            score=0.0,
            grade="indistinct",
            shared_minutes=0,
            total_minutes=0,
            error=str(exc),
        )

    own = _firing_minutes(expr)
    if not own:
        return ContrastResult(
            expression=expression,
            score=0.0,
            grade="indistinct",
            shared_minutes=0,
            total_minutes=0,
        )

    peer_union: set = set()
    for p in peers:
        try:
            peer_union |= _firing_minutes(CronExpression(p))
        except CronParseError:
            pass

    shared = len(own & peer_union)
    score = 1.0 - (shared / len(own)) if own else 0.0
    return ContrastResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        shared_minutes=shared,
        total_minutes=len(own),
    )
