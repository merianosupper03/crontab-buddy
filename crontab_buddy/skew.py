"""Skew analysis: measures how asymmetrically a cron expression fires across a day."""
from dataclasses import dataclass, field
from typing import List, Optional
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class SkewResult:
    expression: str
    score: float  # 0.0 (perfectly symmetric) to 1.0 (fully skewed)
    label: str
    morning_share: float
    afternoon_share: float
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"Skew({self.expression}): error - {self.error}"
        return (
            f"Skew({self.expression}): {self.label} "
            f"[score={self.score:.2f}, AM={self.morning_share:.0%}, PM={self.afternoon_share:.0%}]"
        )


def _grade(score: float) -> str:
    if score < 0.10:
        return "balanced"
    if score < 0.30:
        return "slight"
    if score < 0.55:
        return "moderate"
    if score < 0.80:
        return "heavy"
    return "extreme"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return a flat list of absolute minutes-in-day when the expression fires (hour x 60 + minute)."""
    minute_field = expr.fields[0]
    hour_field = expr.fields[1]

    def expand(field_str: str, lo: int, hi: int) -> List[int]:
        if field_str == "*":
            return list(range(lo, hi + 1))
        values: List[int] = []
        for part in field_str.split(","):
            if "/" in part:
                base, step = part.split("/", 1)
                start = lo if base == "*" else int(base.split("-")[0])
                values.extend(range(start, hi + 1, int(step)))
            elif "-" in part:
                a, b = part.split("-", 1)
                values.extend(range(int(a), int(b) + 1))
            else:
                values.append(int(part))
        return values

    minutes = expand(minute_field, 0, 59)
    hours = expand(hour_field, 0, 23)
    return [h * 60 + m for h in hours for m in minutes]


def assess_skew(expression: str) -> SkewResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return SkewResult(
            expression=expression,
            score=1.0,
            label="extreme",
            morning_share=0.0,
            afternoon_share=0.0,
            error=str(exc),
        )

    firings = _firing_minutes(expr)
    if not firings:
        return SkewResult(expression, 0.0, "balanced", 0.0, 0.0)

    total = len(firings)
    morning = sum(1 for m in firings if m < 720)  # before noon
    afternoon = total - morning
    am_share = morning / total
    pm_share = afternoon / total
    score = abs(am_share - pm_share)
    return SkewResult(
        expression=expression,
        score=round(score, 4),
        label=_grade(score),
        morning_share=round(am_share, 4),
        afternoon_share=round(pm_share, 4),
    )


def batch_skew(expressions: List[str]) -> List[SkewResult]:
    return [assess_skew(e) for e in expressions]
