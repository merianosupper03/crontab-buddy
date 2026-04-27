"""Complexity scoring for cron expressions."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class ComplexityResult:
    expression: str
    score: int
    level: str  # simple / moderate / complex
    reasons: list[str]

    def __str__(self) -> str:
        reasons_str = "; ".join(self.reasons) if self.reasons else "no special patterns"
        return f"[{self.level.upper()}] score={self.score} — {reasons_str}"


def _score_field(field: str) -> tuple[int, list[str]]:
    """Return a (score, reasons) tuple for a single field token."""
    score = 0
    reasons: list[str] = []

    if field == "*":
        return 0, []

    if "," in field:
        count = field.count(",") + 1
        score += count
        reasons.append(f"list with {count} values")

    if "/" in field:
        score += 1
        reasons.append("step expression")

    if "-" in field.lstrip("-"):  # avoid false positive on negative-like strings
        score += 1
        reasons.append("range expression")

    if field not in ("*",) and "," not in field and "/" not in field and "-" not in field:
        score += 0  # plain value — no extra complexity

    return score, reasons


def score_expression(expression: str) -> Optional[ComplexityResult]:
    """Score the complexity of a cron expression.

    Returns None if the expression cannot be parsed.
    """
    try:
        expr = CronExpression(expression)
    except CronParseError:
        return None

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    field_names = ["minute", "hour", "dom", "month", "dow"]

    total_score = 0
    all_reasons: list[str] = []

    for name, field in zip(field_names, fields):
        s, reasons = _score_field(field)
        total_score += s
        for r in reasons:
            all_reasons.append(f"{name}: {r}")

    # penalise both dom and dow being non-wildcard (ambiguous semantics)
    if expr.dom != "*" and expr.dow != "*":
        total_score += 2
        all_reasons.append("both dom and dow are restricted (ambiguous)")

    if total_score <= 1:
        level = "simple"
    elif total_score <= 4:
        level = "moderate"
    else:
        level = "complex"

    return ComplexityResult(
        expression=expression,
        score=total_score,
        level=level,
        reasons=all_reasons,
    )
