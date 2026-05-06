"""Assess how regular/consistent a cron expression's firing pattern is."""

from dataclasses import dataclass
from typing import Optional

from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class RegularityResult:
    expression: str
    score: float  # 0.0 (irregular) to 1.0 (perfectly regular)
    level: str
    description: str
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"RegularityResult({self.expression!r}, error={self.error!r})"
        return (
            f"RegularityResult({self.expression!r}, "
            f"score={self.score:.2f}, level={self.level!r})"
        )


def _grade(score: float) -> str:
    if score >= 0.85:
        return "highly regular"
    if score >= 0.65:
        return "regular"
    if score >= 0.40:
        return "somewhat irregular"
    return "irregular"


def _field_regularity(field: str) -> float:
    """Return a regularity score for a single cron field."""
    if field == "*":
        return 1.0
    if field.isdigit():
        return 1.0
    if "," in field:
        # lists are somewhat regular but less so than a single value
        parts = field.split(",")
        return max(0.3, 1.0 - (len(parts) - 1) * 0.15)
    if "-" in field and "/" not in field:
        return 0.6
    if field.startswith("*/"):
        try:
            step = int(field[2:])
            # step of 1 == wildcard, larger steps are less regular
            return max(0.4, 1.0 - (step - 1) * 0.05)
        except ValueError:
            return 0.4
    if "/" in field:
        return 0.5
    return 0.5


def assess_regularity(expression: str) -> RegularityResult:
    """Assess the regularity of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return RegularityResult(
            expression=expression,
            score=0.0,
            level="irregular",
            description="Invalid expression.",
            error=str(exc),
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    scores = [_field_regularity(f) for f in fields]
    # weight minute and hour more heavily
    weights = [0.30, 0.30, 0.20, 0.10, 0.10]
    score = sum(s * w for s, w in zip(scores, weights))
    score = round(min(1.0, max(0.0, score)), 4)
    level = _grade(score)
    description = (
        f"Expression fires in a {level} pattern "
        f"(score {score:.2f}/1.00)."
    )
    return RegularityResult(
        expression=expression,
        score=score,
        level=level,
        description=description,
    )


def batch_regularity(expressions: list) -> list:
    """Assess regularity for a list of expressions."""
    return [assess_regularity(e) for e in expressions]
