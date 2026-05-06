"""Fidelity scoring: how precisely specified a cron expression is."""

from dataclasses import dataclass
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class FidelityResult:
    expression: str
    score: float  # 0.0 (vague) to 1.0 (fully precise)
    level: str
    details: list

    def __str__(self) -> str:
        return (
            f"Expression : {self.expression}\n"
            f"Fidelity   : {self.level} ({self.score:.2f})\n"
            f"Details    : {', '.join(self.details) if self.details else 'none'}"
        )


def _grade(score: float) -> str:
    if score >= 0.85:
        return "precise"
    if score >= 0.60:
        return "moderate"
    if score >= 0.35:
        return "vague"
    return "unspecified"


def _field_score(value: str) -> float:
    """Return a specificity score for a single cron field."""
    if value == "*":
        return 0.0
    if "/" in value:
        return 0.4
    if "-" in value:
        return 0.6
    if "," in value:
        return 0.75
    # plain integer — fully specified
    return 1.0


def assess_fidelity(expression: str) -> FidelityResult:
    """Score how precisely a cron expression pins down its schedule."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return FidelityResult(
            expression=expression,
            score=0.0,
            level="unspecified",
            details=[f"parse error: {exc}"],
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]
    scores = [_field_score(f) for f in fields]
    overall = sum(scores) / len(scores)

    details = [
        f"{name}={val} ({sc:.2f})"
        for name, val, sc in zip(names, fields, scores)
        if sc < 1.0
    ]

    return FidelityResult(
        expression=expression,
        score=round(overall, 4),
        level=_grade(overall),
        details=details,
    )
