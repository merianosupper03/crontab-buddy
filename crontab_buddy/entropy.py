"""Entropy scoring for cron expressions — measures how 'random' or unpredictable a schedule feels."""

from dataclasses import dataclass
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class EntropyResult:
    expression: str
    score: float  # 0.0 (fully predictable) to 1.0 (highly irregular)
    level: str
    notes: list

    def __str__(self) -> str:
        note_str = "; ".join(self.notes) if self.notes else "none"
        return f"Entropy: {self.score:.2f} ({self.level}) | Notes: {note_str}"


def _field_entropy(value: str, field_range: int) -> float:
    """Estimate entropy contribution of a single field."""
    if value == "*":
        return 0.0
    if "," in value:
        parts = value.split(",")
        return min(len(parts) / field_range, 1.0) * 0.8
    if "-" in value and "/" not in value:
        lo, hi = value.split("-", 1)
        try:
            span = int(hi) - int(lo) + 1
            return min(span / field_range, 1.0) * 0.5
        except ValueError:
            return 0.3
    if value.startswith("*/"):
        try:
            step = int(value[2:])
            return max(0.1, 1.0 - step / field_range)
        except ValueError:
            return 0.2
    # plain number — very predictable
    return 0.15


_RANGES = [60, 24, 31, 12, 7]
_WEIGHTS = [0.25, 0.25, 0.2, 0.2, 0.1]


def compute_entropy(expression: str) -> EntropyResult:
    """Compute an entropy score for a cron expression."""
    notes = []
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return EntropyResult(
            expression=expression,
            score=0.0,
            level="unknown",
            notes=[f"parse error: {exc}"],
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    raw_score = sum(
        _field_entropy(f, r) * w
        for f, r, w in zip(fields, _RANGES, _WEIGHTS)
    )
    score = round(min(raw_score, 1.0), 4)

    if expr.dom != "*" and expr.dow != "*":
        notes.append("both DOM and DOW set — behaviour varies by system")
        score = min(score + 0.1, 1.0)

    if score < 0.15:
        level = "predictable"
    elif score < 0.4:
        level = "moderate"
    elif score < 0.7:
        level = "irregular"
    else:
        level = "chaotic"
        notes.append("high entropy — consider simplifying")

    return EntropyResult(expression=expression, score=score, level=level, notes=notes)
