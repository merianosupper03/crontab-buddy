"""coverage_score.py — score how well a cron expression covers a 24-hour day."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


_GRADES = [
    (0.90, "blanket"),
    (0.70, "broad"),
    (0.50, "moderate"),
    (0.30, "sparse"),
    (0.10, "thin"),
    (0.00, "bare"),
]


def _grade(score: float) -> str:
    for threshold, label in _GRADES:
        if score >= threshold:
            return label
    return "bare"


def _covered_hours(expr: CronExpression) -> List[int]:
    """Return list of hours (0-23) that the expression can fire in."""
    hour_field = expr.fields[1]
    covered = []
    if hour_field == "*":
        return list(range(24))
    for part in hour_field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            step_val = int(step)
            covered.extend(range(start, 24, step_val))
        elif "-" in part:
            lo, hi = part.split("-", 1)
            covered.extend(range(int(lo), int(hi) + 1))
        else:
            covered.append(int(part))
    return sorted(set(covered))


@dataclass
class CoverageScoreResult:
    expression: str
    score: float
    grade: str
    covered_hours: List[int]
    total_hours: int = 24
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"CoverageScore({self.expression!r}) ERROR: {self.error}"
        return (
            f"CoverageScore({self.expression!r}) "
            f"score={self.score:.2f} grade={self.grade} "
            f"covered={len(self.covered_hours)}/{self.total_hours}h"
        )


def compute_coverage_score(expression: str) -> CoverageScoreResult:
    """Compute how broadly a cron expression covers the 24-hour clock."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return CoverageScoreResult(
            expression=expression,
            score=0.0,
            grade="bare",
            covered_hours=[],
            error=str(exc),
        )

    hours = _covered_hours(expr)
    score = round(len(hours) / 24, 4)
    return CoverageScoreResult(
        expression=expression,
        score=score,
        grade=_grade(score),
        covered_hours=hours,
    )


def batch_coverage_score(expressions: List[str]) -> List[CoverageScoreResult]:
    return [compute_coverage_score(e) for e in expressions]
