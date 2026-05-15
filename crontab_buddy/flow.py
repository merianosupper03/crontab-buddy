"""Flow analysis: measures how smoothly a cron expression transitions
between firing windows over a 24-hour period."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "fluid"
    if score >= 0.65:
        return "smooth"
    if score >= 0.45:
        return "uneven"
    if score >= 0.25:
        return "choppy"
    return "erratic"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return sorted list of minutes-of-day (0..1439) when expr fires."""
    minutes: List[int] = []
    minute_field = expr.minute
    hour_field = expr.hour

    def _expand(field_str: str, lo: int, hi: int) -> List[int]:
        if field_str == "*":
            return list(range(lo, hi + 1))
        result = []
        for part in field_str.split(","):
            if "/" in part:
                base, step = part.split("/", 1)
                start = lo if base == "*" else int(base.split("-")[0])
                result.extend(range(start, hi + 1, int(step)))
            elif "-" in part:
                a, b = part.split("-", 1)
                result.extend(range(int(a), int(b) + 1))
            else:
                result.append(int(part))
        return result

    hours = _expand(hour_field, 0, 23)
    mins = _expand(minute_field, 0, 59)
    for h in hours:
        for m in mins:
            minutes.append(h * 60 + m)
    return sorted(set(minutes))


@dataclass
class FlowResult:
    expression: str
    score: float
    grade: str
    transitions: int
    total_gaps: int
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"FlowResult(error={self.error})"
        return (
            f"FlowResult(expression={self.expression!r}, "
            f"grade={self.grade!r}, score={self.score:.3f}, "
            f"transitions={self.transitions})"
        )


def assess_flow(expression: str) -> FlowResult:
    """Assess how fluidly an expression flows across the day."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return FlowResult(
            expression=expression,
            score=0.0,
            grade="erratic",
            transitions=0,
            total_gaps=0,
            error=str(exc),
        )

    firing = _firing_minutes(expr)
    if len(firing) <= 1:
        return FlowResult(
            expression=expression,
            score=0.0,
            grade="erratic",
            transitions=len(firing),
            total_gaps=0,
        )

    gaps = [firing[i + 1] - firing[i] for i in range(len(firing) - 1)]
    if not gaps:
        return FlowResult(
            expression=expression,
            score=1.0,
            grade="fluid",
            transitions=len(firing),
            total_gaps=0,
        )

    mean_gap = sum(gaps) / len(gaps)
    variance = sum((g - mean_gap) ** 2 for g in gaps) / len(gaps)
    std_dev = variance ** 0.5
    # Normalise: lower std_dev relative to mean_gap => higher score
    cv = std_dev / mean_gap if mean_gap > 0 else 1.0
    score = max(0.0, min(1.0, 1.0 - (cv / 3.0)))
    return FlowResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        transitions=len(firing),
        total_gaps=len(gaps),
    )


def batch_flow(expressions: List[str]) -> List[FlowResult]:
    return [assess_flow(e) for e in expressions]
