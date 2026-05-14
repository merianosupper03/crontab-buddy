"""Texture analysis: measures the structural variety of a cron expression."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


TEXTURE_GRADES = [
    (0.85, "rich"),
    (0.65, "varied"),
    (0.45, "moderate"),
    (0.25, "plain"),
    (0.0,  "flat"),
]


def _grade(score: float) -> str:
    for threshold, label in TEXTURE_GRADES:
        if score >= threshold:
            return label
    return "flat"


def _field_texture(value: str) -> float:
    """Score a single field by how many distinct constructs it uses."""
    if value == "*":
        return 0.2
    score = 0.0
    if "," in value:
        score += 0.35
    if "-" in value:
        score += 0.3
    if "/" in value:
        score += 0.25
    if score == 0.0:
        score = 0.5  # plain integer — moderately textured
    return min(score, 1.0)


@dataclass
class TextureResult:
    expression: str
    score: float
    grade: str
    scores: dict = field(default_factory=dict)
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"TextureResult(error={self.error})"
        return f"TextureResult(expression={self.expression!r}, score={self.score:.3f}, grade={self.grade})"


def assess_texture(expression: str) -> TextureResult:
    """Assess the structural texture of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return TextureResult(expression=expression, score=0.0, grade="flat", error=str(exc))

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]
    scores = {name: _field_texture(val) for name, val in zip(names, fields)}
    overall = sum(scores.values()) / len(scores)
    return TextureResult(
        expression=expression,
        score=round(overall, 4),
        grade=_grade(overall),
        scores=scores,
    )


def batch_texture(expressions: list[str]) -> list[TextureResult]:
    return [assess_texture(e) for e in expressions]
