"""Curvature: measures how sharply a cron expression changes firing rate across hours."""

from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


GRADES = [
    (0.85, "steep"),
    (0.60, "curved"),
    (0.35, "gradual"),
    (0.10, "gentle"),
    (0.0,  "flat"),
]


def _grade(score: float) -> str:
    for threshold, label in GRADES:
        if score >= threshold:
            return label
    return "flat"


def _firing_minutes_per_hour(expr: CronExpression) -> list[int]:
    """Return count of firing minutes for each of the 24 hours."""
    counts = []
    minute_field = expr.fields[0]
    hour_field = expr.fields[1]

    minutes: list[int] = []
    if minute_field == "*":
        minutes = list(range(60))
    elif minute_field.startswith("*/"):
        step = int(minute_field[2:])
        minutes = list(range(0, 60, step))
    elif "-" in minute_field:
        a, b = minute_field.split("-")
        minutes = list(range(int(a), int(b) + 1))
    elif "," in minute_field:
        minutes = [int(x) for x in minute_field.split(",")]
    else:
        minutes = [int(minute_field)]

    active_hours: list[int] = []
    if hour_field == "*":
        active_hours = list(range(24))
    elif hour_field.startswith("*/"):
        step = int(hour_field[2:])
        active_hours = list(range(0, 24, step))
    elif "-" in hour_field:
        a, b = hour_field.split("-")
        active_hours = list(range(int(a), int(b) + 1))
    elif "," in hour_field:
        active_hours = [int(x) for x in hour_field.split(",")]
    else:
        active_hours = [int(hour_field)]

    for h in range(24):
        counts.append(len(minutes) if h in active_hours else 0)
    return counts


class CurvatureResult:
    def __init__(self, expression: str, score: float, grade: str, error: Optional[str] = None):
        self.expression = expression
        self.score = score
        self.grade = grade
        self.error = error

    def __str__(self) -> str:
        if self.error:
            return f"CurvatureResult({self.expression!r}, error={self.error!r})"
        return f"CurvatureResult({self.expression!r}, score={self.score:.3f}, grade={self.grade!r})"


def assess_curvature(expression: str) -> CurvatureResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as e:
        return CurvatureResult(expression, 0.0, "flat", error=str(e))

    counts = _firing_minutes_per_hour(expr)
    if max(counts) == 0:
        return CurvatureResult(expression, 0.0, "flat")

    diffs = [abs(counts[i + 1] - counts[i]) for i in range(len(counts) - 1)]
    max_possible = max(counts)
    avg_diff = sum(diffs) / len(diffs) if diffs else 0.0
    score = min(avg_diff / max_possible, 1.0) if max_possible > 0 else 0.0
    return CurvatureResult(expression, round(score, 4), _grade(score))


def batch_curvature(expressions: list[str]) -> list[CurvatureResult]:
    return [assess_curvature(e) for e in expressions]
