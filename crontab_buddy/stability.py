"""Assess the stability of a cron expression based on its recurrence pattern."""

from dataclasses import dataclass
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds


STABILITY_LEVELS = ("unstable", "fragile", "moderate", "stable", "rock-solid")


@dataclass
class StabilityResult:
    expression: str
    score: float  # 0.0 – 1.0
    level: str
    interval_seconds: int | None
    notes: list

    def __str__(self) -> str:
        notes_str = "; ".join(self.notes) if self.notes else "none"
        return (
            f"StabilityResult(expression={self.expression!r}, "
            f"score={self.score:.2f}, level={self.level!r}, notes=[{notes_str}])"
        )


def _grade(score: float) -> str:
    if score >= 0.85:
        return "rock-solid"
    if score >= 0.65:
        return "stable"
    if score >= 0.45:
        return "moderate"
    if score >= 0.25:
        return "fragile"
    return "unstable"


def assess_stability(expression: str) -> StabilityResult:
    notes = []

    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return StabilityResult(
            expression=expression,
            score=0.0,
            level="unstable",
            interval_seconds=None,
            notes=[f"parse error: {exc}"],
        )

    interval = recurrence_interval_seconds(expression)
    score = 0.5

    if interval is None:
        notes.append("could not determine recurrence interval")
        score = 0.3
    elif interval < 60:
        notes.append("sub-minute interval is extremely volatile")
        score = 0.05
    elif interval < 300:
        notes.append("fires more than once every 5 minutes")
        score = 0.2
    elif interval < 3600:
        score = 0.45
    elif interval < 86400:
        score = 0.7
    else:
        score = 0.9

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    list_count = sum(1 for f in fields if "," in f)
    if list_count >= 3:
        notes.append("many list fields reduce predictability")
        score = max(0.0, score - 0.1 * list_count)

    wildcard_count = sum(1 for f in fields if f == "*")
    if wildcard_count == 5:
        notes.append("all wildcards — runs every minute")
        score = 0.05

    score = round(min(1.0, max(0.0, score)), 4)
    return StabilityResult(
        expression=expression,
        score=score,
        level=_grade(score),
        interval_seconds=interval,
        notes=notes,
    )
