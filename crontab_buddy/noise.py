"""Noise assessment for cron expressions.

Measures how much 'noise' (unpredictability / lack of structure) a cron
expression introduces relative to a clean, well-defined schedule.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "deafening"
    if score >= 0.70:
        return "loud"
    if score >= 0.50:
        return "moderate"
    if score >= 0.30:
        return "faint"
    if score >= 0.10:
        return "whisper"
    return "silent"


def _field_noise(value: str) -> float:
    """Return a noise contribution [0, 1] for a single cron field."""
    if value == "*":
        return 0.6  # fully open — inherently noisy
    if "," in value:
        parts = value.split(",")
        return min(0.4 + 0.1 * len(parts), 0.9)
    if "-" in value and "/" in value:
        return 0.5
    if "-" in value:
        return 0.35
    if value.startswith("*/"):
        try:
            step = int(value[2:])
            return max(0.0, 0.5 - step / 120.0)
        except ValueError:
            return 0.4
    if "/" in value:
        return 0.3
    # plain integer — very quiet
    return 0.0


@dataclass
class NoiseResult:
    expression: str
    score: float
    grade: str
    scores: dict = field(default_factory=dict)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"NoiseResult(error={self.error!r})"
        return (
            f"NoiseResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r})"
        )


def assess_noise(expression: str) -> NoiseResult:
    """Assess the noise level of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return NoiseResult(
            expression=expression,
            score=0.0,
            grade="silent",
            error=str(exc),
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]
    weights = [0.30, 0.25, 0.20, 0.10, 0.15]

    scores = {name: _field_noise(f) for name, f in zip(names, fields)}
    overall = sum(scores[n] * w for n, w in zip(names, weights))
    overall = round(min(max(overall, 0.0), 1.0), 4)

    return NoiseResult(
        expression=expression,
        score=overall,
        grade=_grade(overall),
        scores=scores,
    )


def batch_noise(expressions: list[str]) -> list[NoiseResult]:
    return [assess_noise(e) for e in expressions]
