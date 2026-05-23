"""Evenness: measures how evenly distributed a cron expression's firing times are."""
from __future__ import annotations
import statistics
from typing import List, Optional
from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.90:
        return "perfectly even"
    if score >= 0.75:
        return "mostly even"
    if score >= 0.55:
        return "somewhat uneven"
    if score >= 0.30:
        return "uneven"
    return "highly uneven"


def _firing_minutes(expr: CronExpression) -> List[int]:
    minute_field = expr.fields[0]
    if minute_field == "*":
        return list(range(60))
    minutes: List[int] = []
    for part in minute_field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            minutes.extend(range(start, 60, int(step)))
        elif "-" in part:
            lo, hi = part.split("-", 1)
            minutes.extend(range(int(lo), int(hi) + 1))
        else:
            minutes.append(int(part))
    return sorted(set(minutes))


class EvennessResult:
    def __init__(self, expression: str, score: float, grade: str, error: Optional[str] = None):
        self.expression = expression
        self.score = score
        self.grade = grade
        self.error = error

    def __str__(self) -> str:
        if self.error:
            return f"Evenness({self.expression!r}): error={self.error}"
        return f"Evenness({self.expression!r}): {self.grade} ({self.score:.3f})"


def assess_evenness(expression: str) -> EvennessResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return EvennessResult(expression, 0.0, "highly uneven", error=str(exc))

    minutes = _firing_minutes(expr)
    if len(minutes) <= 1:
        score = 0.0
        return EvennessResult(expression, score, _grade(score))

    gaps = [minutes[i + 1] - minutes[i] for i in range(len(minutes) - 1)]
    wrap_gap = (60 - minutes[-1]) + minutes[0]
    gaps.append(wrap_gap)

    mean_gap = statistics.mean(gaps)
    if mean_gap == 0:
        score = 1.0
    else:
        stdev = statistics.pstdev(gaps)
        cv = stdev / mean_gap
        score = max(0.0, min(1.0, 1.0 - cv))

    return EvennessResult(expression, round(score, 4), _grade(score))


def batch_evenness(expressions: List[str]) -> List[EvennessResult]:
    return [assess_evenness(e) for e in expressions]
