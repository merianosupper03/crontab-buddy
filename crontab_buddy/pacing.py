"""Pacing: assess how evenly a cron expression distributes its runs across a day."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


GRADES = [
    (0.90, "metered"),
    (0.70, "steady"),
    (0.50, "uneven"),
    (0.25, "choppy"),
    (0.0,  "erratic"),
]


def _grade(score: float) -> str:
    for threshold, label in GRADES:
        if score >= threshold:
            return label
    return "erratic"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return all minutes-of-day (0-1439) when the expression fires."""
    minutes_field = expr.fields[0]
    hours_field = expr.fields[1]

    def expand(field_str: str, max_val: int) -> List[int]:
        if field_str == "*":
            return list(range(max_val))
        result = set()
        for part in field_str.split(","):
            if "/" in part:
                base, step = part.split("/", 1)
                rng = range(max_val) if base == "*" else range(*[int(x) for x in base.split("-", 1)] + [max_val])[:1] or range(int(base.split("-")[0]), max_val)
                if "-" in base:
                    lo, hi = base.split("-", 1)
                    rng = range(int(lo), int(hi) + 1)
                else:
                    rng = range(0 if base == "*" else int(base), max_val)
                result.update(rng[::int(step)])
            elif "-" in part:
                lo, hi = part.split("-", 1)
                result.update(range(int(lo), int(hi) + 1))
            else:
                result.add(int(part))
        return sorted(result)

    hours = expand(hours_field, 24)
    mins = expand(minutes_field, 60)
    return sorted(h * 60 + m for h in hours for m in mins)


@dataclass
class PacingResult:
    expression: str
    score: float
    grade: str
    fires_per_day: int
    hourly_variance: float
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"PacingResult(error={self.error!r})"
        return (
            f"PacingResult(expression={self.expression!r}, "
            f"grade={self.grade!r}, score={self.score:.3f}, "
            f"fires_per_day={self.fires_per_day})"
        )


def assess_pacing(expression: str) -> PacingResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return PacingResult(expression=expression, score=0.0, grade="erratic",
                            fires_per_day=0, hourly_variance=0.0, error=str(exc))

    firing = _firing_minutes(expr)
    if not firing:
        return PacingResult(expression=expression, score=0.0, grade="erratic",
                            fires_per_day=0, hourly_variance=0.0)

    hourly_counts = [0] * 24
    for m in firing:
        hourly_counts[m // 60] += 1

    active_hours = [c for c in hourly_counts if c > 0]
    if len(active_hours) <= 1:
        score = 0.1
    else:
        mean = sum(active_hours) / len(active_hours)
        variance = sum((c - mean) ** 2 for c in active_hours) / len(active_hours)
        cv = (variance ** 0.5) / mean if mean else 1.0
        score = max(0.0, min(1.0, 1.0 - cv))

    hourly_variance = sum((c - (sum(hourly_counts) / 24)) ** 2 for c in hourly_counts) / 24

    return PacingResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        fires_per_day=len(firing),
        hourly_variance=round(hourly_variance, 4),
    )


def batch_pacing(expressions: List[str]) -> List[PacingResult]:
    return [assess_pacing(e) for e in expressions]
