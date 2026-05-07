"""Polarity: assess whether a cron expression leans toward daytime or nighttime scheduling."""

from dataclasses import dataclass
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError

DAYTIME_HOURS = set(range(6, 20))   # 06:00 – 19:59
NIGHTTIME_HOURS = set(range(20, 24)) | set(range(0, 6))  # 20:00 – 05:59


@dataclass
class PolarityResult:
    expression: str
    polarity: str          # "daytime", "nighttime", "neutral", "all-day", "error"
    day_hours: int
    night_hours: int
    score: float           # -1.0 (full night) … +1.0 (full day)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"{self.expression}: error – {self.error}"
        return (
            f"{self.expression}: {self.polarity} "
            f"(day={self.day_hours}h, night={self.night_hours}h, score={self.score:.2f})"
        )


def _grade(score: float) -> str:
    if score >= 0.8:
        return "daytime"
    if score <= -0.8:
        return "nighttime"
    if -0.1 <= score <= 0.1:
        return "neutral"
    if score > 0.1:
        return "daytime"
    return "nighttime"


def assess_polarity(expression: str) -> PolarityResult:
    """Assess the daytime/nighttime polarity of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return PolarityResult(
            expression=expression,
            polarity="error",
            day_hours=0,
            night_hours=0,
            score=0.0,
            error=str(exc),
        )

    hour_field = expr.fields[1]

    if hour_field == "*":
        active_hours = set(range(24))
    elif "/" in hour_field and hour_field.startswith("*/"):
        step = int(hour_field.split("/")[1])
        active_hours = set(range(0, 24, step))
    elif "-" in hour_field:
        parts = hour_field.split("-")
        active_hours = set(range(int(parts[0]), int(parts[1]) + 1))
    elif "," in hour_field:
        active_hours = {int(h) for h in hour_field.split(",")}
    else:
        try:
            active_hours = {int(hour_field)}
        except ValueError:
            active_hours = set(range(24))

    day = len(active_hours & DAYTIME_HOURS)
    night = len(active_hours & NIGHTTIME_HOURS)
    total = day + night
    score = (day - night) / total if total else 0.0

    return PolarityResult(
        expression=expression,
        polarity=_grade(score),
        day_hours=day,
        night_hours=night,
        score=round(score, 4),
    )


def batch_polarity(expressions: list) -> list:
    """Assess polarity for a list of expressions."""
    return [assess_polarity(expr) for expr in expressions]
