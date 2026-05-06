"""Affinity scoring — how well two cron expressions complement each other
without overlapping excessively or leaving large gaps."""

from dataclasses import dataclass, field
from typing import List

from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.scheduler import next_runs


@dataclass
class AffinityResult:
    expression_a: str
    expression_b: str
    score: float  # 0.0 – 1.0
    grade: str
    overlap_count: int
    notes: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [
            f"Affinity: {self.expression_a!r} <-> {self.expression_b!r}",
            f"  Score : {self.score:.2f}  Grade: {self.grade}",
            f"  Overlap runs (24 h): {self.overlap_count}",
        ]
        for note in self.notes:
            lines.append(f"  * {note}")
        return "\n".join(lines)


def _grade(score: float) -> str:
    if score >= 0.85:
        return "Excellent"
    if score >= 0.65:
        return "Good"
    if score >= 0.40:
        return "Fair"
    return "Poor"


def assess_affinity(expr_a: str, expr_b: str, hours: int = 24) -> AffinityResult:
    """Return an AffinityResult comparing two cron expressions."""
    notes: List[str] = []

    try:
        CronExpression(expr_a)
    except CronParseError as exc:
        return AffinityResult(expr_a, expr_b, 0.0, "Poor", 0,
                              [f"Invalid expression A: {exc}"])

    try:
        CronExpression(expr_b)
    except CronParseError as exc:
        return AffinityResult(expr_a, expr_b, 0.0, "Poor", 0,
                              [f"Invalid expression B: {exc}"])

    from datetime import datetime
    start = datetime(2024, 1, 1, 0, 0)
    runs_a = set(next_runs(expr_a, count=hours * 60, start=start))
    runs_b = set(next_runs(expr_b, count=hours * 60, start=start))

    overlap = runs_a & runs_b
    total = len(runs_a) + len(runs_b)
    overlap_count = len(overlap)

    if total == 0:
        return AffinityResult(expr_a, expr_b, 0.5, "Fair", 0,
                              ["Neither expression fires in the window."])

    overlap_ratio = overlap_count / (total / 2) if total else 0.0

    # High overlap is bad (redundant), zero overlap is also not ideal
    if overlap_ratio > 0.9:
        score = 0.20
        notes.append("Expressions fire almost simultaneously — likely redundant.")
    elif overlap_ratio == 0.0:
        score = 0.55
        notes.append("No shared fire times — good separation but no coordination.")
    else:
        score = 1.0 - overlap_ratio * 0.8

    if score > 1.0:
        score = 1.0

    grade = _grade(score)
    return AffinityResult(expr_a, expr_b, round(score, 4), grade, overlap_count, notes)
