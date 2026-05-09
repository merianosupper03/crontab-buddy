"""Resonance: measure how well two cron expressions 'resonate' (share firing patterns periodically)."""

from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class ResonanceResult:
    expression_a: str
    expression_b: str
    score: float
    grade: str
    shared_minutes: int
    total_minutes: int
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"Resonance error: {self.error}"
        return (
            f"Resonance between '{self.expression_a}' and '{self.expression_b}': "
            f"{self.grade} ({self.score:.2f}) — "
            f"{self.shared_minutes}/{self.total_minutes} shared minutes/day"
        )


def _grade(score: float) -> str:
    if score >= 0.9:
        return "harmonic"
    if score >= 0.7:
        return "resonant"
    if score >= 0.4:
        return "partial"
    if score >= 0.1:
        return "faint"
    return "silent"


def _firing_minutes(expr: CronExpression) -> set:
    """Return the set of (hour, minute) tuples that fire in a 24h window."""
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


def assess_resonance(expr_a: str, expr_b: str) -> ResonanceResult:
    try:
        ca = CronExpression(expr_a)
    except CronParseError as e:
        return ResonanceResult(expr_a, expr_b, 0.0, "silent", 0, 0, error=str(e))
    try:
        cb = CronExpression(expr_b)
    except CronParseError as e:
        return ResonanceResult(expr_a, expr_b, 0.0, "silent", 0, 0, error=str(e))

    set_a = _firing_minutes(ca)
    set_b = _firing_minutes(cb)
    shared = len(set_a & set_b)
    total = len(set_a | set_b)
    score = shared / total if total > 0 else 0.0
    return ResonanceResult(
        expression_a=expr_a,
        expression_b=expr_b,
        score=round(score, 4),
        grade=_grade(score),
        shared_minutes=shared,
        total_minutes=total,
    )


def batch_resonance(base: str, others: list) -> list:
    return [assess_resonance(base, o) for o in others]
