"""balance.py — assess how evenly a cron expression distributes load across time."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List

from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class BalanceResult:
    expression: str
    score: float          # 0.0 (very unbalanced) .. 1.0 (perfectly balanced)
    grade: str
    notes: List[str]

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Balance    : {self.score:.2f} ({self.grade})",
        ]
        for note in self.notes:
            lines.append(f"  • {note}")
        return "\n".join(lines)


def _grade(score: float) -> str:
    if score >= 0.85:
        return "excellent"
    if score >= 0.65:
        return "good"
    if score >= 0.40:
        return "fair"
    return "poor"


def _field_spread(field: str, lo: int, hi: int) -> float:
    """Return a 0-1 spread score for a single cron field string."""
    total = hi - lo + 1
    if field == "*":
        return 1.0
    if "/" in field:
        base, step = field.split("/", 1)
        try:
            s = int(step)
            return min(1.0, s / total) if s > 1 else 1.0
        except ValueError:
            return 0.5
    if "," in field:
        parts = field.split(",")
        return min(1.0, len(parts) / total)
    if "-" in field:
        a, b = field.split("-", 1)
        try:
            span = int(b) - int(a) + 1
            return min(1.0, span / total)
        except ValueError:
            return 0.5
    # exact value — single point in time
    return 1.0 / total


def assess_balance(expression: str) -> BalanceResult:
    notes: List[str] = []
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return BalanceResult(expression=expression, score=0.0, grade="poor",
                             notes=[f"Invalid expression: {exc}"])

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]
    names  = ["minute", "hour", "day-of-month", "month", "day-of-week"]

    spreads = []
    for field, (lo, hi), name in zip(fields, ranges, names):
        s = _field_spread(field, lo, hi)
        spreads.append(s)
        if s < 0.10:
            notes.append(f"{name} is highly concentrated (spread={s:.2f})")

    score = sum(spreads) / len(spreads)
    if not notes:
        notes.append("Load appears reasonably distributed across all fields.")

    return BalanceResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        notes=notes,
    )
