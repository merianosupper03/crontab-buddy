"""Conductance: measures how readily a cron expression 'passes through' time
based on the ratio of active minutes to total minutes in a day."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from crontab_buddy.parser import CronExpression, CronParseError

_GRADES = [
    (0.90, "superconducting"),
    (0.70, "highly conductive"),
    (0.40, "conductive"),
    (0.15, "resistive"),
    (0.02, "low conductance"),
    (0.00, "insulating"),
]

TOTAL_MINUTES_PER_DAY = 1440


def _grade(score: float) -> str:
    for threshold, label in _GRADES:
        if score >= threshold:
            return label
    return "insulating"


def _firing_minutes(expr: CronExpression) -> int:
    """Estimate distinct (minute, hour) combos that fire in a day."""
    def expand(field_str: str, lo: int, hi: int) -> list:
        if field_str == "*":
            return list(range(lo, hi + 1))
        results = set()
        for part in field_str.split(","):
            if "/" in part:
                base, step = part.split("/", 1)
                step = int(step)
                start = lo if base == "*" else int(base.split("-")[0])
                end = hi if base == "*" else (int(base.split("-")[1]) if "-" in base else start)
                results.update(range(start, end + 1, step))
            elif "-" in part:
                a, b = part.split("-", 1)
                results.update(range(int(a), int(b) + 1))
            else:
                results.add(int(part))
        return list(results)

    minutes = expand(expr.minute, 0, 59)
    hours = expand(expr.hour, 0, 23)
    return len(minutes) * len(hours)


@dataclass
class ConductanceResult:
    expression: str
    score: float
    grade: str
    active_minutes: int
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"ConductanceResult(error={self.error!r})"
        return (
            f"ConductanceResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r}, "
            f"active_minutes={self.active_minutes})"
        )


def assess_conductance(expression: str) -> ConductanceResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ConductanceResult(
            expression=expression,
            score=0.0,
            grade="insulating",
            active_minutes=0,
            error=str(exc),
        )
    active = _firing_minutes(expr)
    score = round(min(active / TOTAL_MINUTES_PER_DAY, 1.0), 6)
    return ConductanceResult(
        expression=expression,
        score=score,
        grade=_grade(score),
        active_minutes=active,
    )


def batch_conductance(expressions: list) -> list:
    return [assess_conductance(e) for e in expressions]
