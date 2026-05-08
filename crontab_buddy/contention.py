"""Contention analysis: detect scheduling conflicts between cron expressions."""

from dataclasses import dataclass, field
from typing import List, Optional
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class ContentionResult:
    expression_a: str
    expression_b: str
    overlap_minutes: int
    score: float  # 0.0 = no contention, 1.0 = full contention
    grade: str
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"Contention [{self.expression_a} vs {self.expression_b}]: error — {self.error}"
        return (
            f"Contention [{self.expression_a} vs {self.expression_b}]: "
            f"{self.grade} (score={self.score:.2f}, overlap={self.overlap_minutes} min/day)"
        )


def _grade(score: float) -> str:
    if score >= 0.8:
        return "critical"
    if score >= 0.5:
        return "high"
    if score >= 0.2:
        return "moderate"
    if score > 0.0:
        return "low"
    return "none"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return list of (hour*60+minute) values that fire within a single day."""
    minutes_field = expr.fields[0]
    hours_field = expr.fields[1]

    def expand(field_str: str, lo: int, hi: int) -> List[int]:
        if field_str == "*":
            return list(range(lo, hi + 1))
        result = set()
        for part in field_str.split(","):
            if "/" in part:
                base, step = part.split("/", 1)
                start = lo if base == "*" else int(base.split("-")[0])
                end = hi if base == "*" else (int(base.split("-")[1]) if "-" in base else start)
                result.update(range(start, end + 1, int(step)))
            elif "-" in part:
                a, b = part.split("-", 1)
                result.update(range(int(a), int(b) + 1))
            else:
                result.add(int(part))
        return sorted(result)

    mins = expand(minutes_field, 0, 59)
    hrs = expand(hours_field, 0, 23)
    return [h * 60 + m for h in hrs for m in mins]


def assess_contention(expr_a: str, expr_b: str) -> ContentionResult:
    try:
        ca = CronExpression(expr_a)
    except CronParseError as e:
        return ContentionResult(expr_a, expr_b, 0, 0.0, "none", error=str(e))
    try:
        cb = CronExpression(expr_b)
    except CronParseError as e:
        return ContentionResult(expr_a, expr_b, 0, 0.0, "none", error=str(e))

    mins_a = set(_firing_minutes(ca))
    mins_b = set(_firing_minutes(cb))
    overlap = len(mins_a & mins_b)
    total = len(mins_a | mins_b) or 1
    score = round(overlap / total, 4)
    return ContentionResult(
        expression_a=expr_a,
        expression_b=expr_b,
        overlap_minutes=overlap,
        score=score,
        grade=_grade(score),
    )
