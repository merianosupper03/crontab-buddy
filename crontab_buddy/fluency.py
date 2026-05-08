"""Fluency assessment: how naturally readable a cron expression is."""
from dataclasses import dataclass, field
from typing import List
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class FluencyResult:
    expression: str
    score: float
    grade: str
    notes: List[str] = field(default_factory=list)
    error: str = ""

    def __str__(self) -> str:
        if self.error:
            return f"FluencyResult({self.expression!r}, error={self.error!r})"
        return f"FluencyResult({self.expression!r}, grade={self.grade!r}, score={self.score:.2f})"


def _grade(score: float) -> str:
    if score >= 0.85:
        return "eloquent"
    if score >= 0.65:
        return "clear"
    if score >= 0.45:
        return "readable"
    if score >= 0.25:
        return "cryptic"
    return "opaque"


def _field_fluency(value: str) -> float:
    """Score a single field 0.0–1.0 based on how easy it is to read."""
    if value == "*":
        return 1.0
    if value.isdigit():
        return 0.95
    if "/" in value and value.startswith("*/"):
        step = value.split("/", 1)[1]
        if step.isdigit():
            return 0.75
        return 0.4
    if "-" in value and "," not in value:
        return 0.6
    if "," in value:
        parts = value.split(",")
        if all(p.isdigit() for p in parts):
            return max(0.3, 0.7 - len(parts) * 0.05)
        return 0.25
    return 0.35


def assess_fluency(expression: str) -> FluencyResult:
    """Assess how fluent / readable a cron expression is."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return FluencyResult(expression=expression, score=0.0, grade="opaque", error=str(exc))

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    scores = [_field_fluency(f) for f in fields]
    avg = sum(scores) / len(scores)

    notes = []
    if expr.dom != "*" and expr.dow != "*":
        notes.append("Both DOM and DOW are set, which can be ambiguous.")
        avg = max(0.0, avg - 0.1)
    if any("," in f and len(f.split(",")) > 4 for f in fields):
        notes.append("Long comma-separated lists reduce readability.")
        avg = max(0.0, avg - 0.05)

    avg = round(min(1.0, max(0.0, avg)), 4)
    return FluencyResult(expression=expression, score=avg, grade=_grade(avg), notes=notes)


def batch_fluency(expressions: List[str]) -> List[FluencyResult]:
    return [assess_fluency(e) for e in expressions]
