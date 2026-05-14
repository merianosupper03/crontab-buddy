"""Topology analysis: assess structural relationships between cron fields."""

from dataclasses import dataclass, field
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


GRADE_MAP = [
    (0.85, "hierarchical"),
    (0.65, "layered"),
    (0.45, "flat"),
    (0.20, "sparse"),
    (0.0,  "disconnected"),
]


def _grade(score: float) -> str:
    for threshold, label in GRADE_MAP:
        if score >= threshold:
            return label
    return "disconnected"


def _field_constraint(value: str) -> float:
    """Return a 0..1 score for how constrained a single field is."""
    if value == "*":
        return 0.0
    if "," in value:
        parts = value.split(",")
        return min(1.0, 0.4 + 0.1 * len(parts))
    if "-" in value:
        lo, hi = value.split("-", 1)
        try:
            span = int(hi) - int(lo)
            return max(0.1, 1.0 - span / 60.0)
        except ValueError:
            return 0.3
    if "/" in value:
        _, step = value.split("/", 1)
        try:
            return min(0.8, 1.0 / max(1, int(step)))
        except ValueError:
            return 0.3
    return 1.0


@dataclass
class TopologyResult:
    expression: str
    score: float
    grade: str
    field_scores: dict
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"TopologyResult(error={self.error})"
        return (
            f"TopologyResult(expression={self.expression!r}, "
            f"score={self.score:.3f}, grade={self.grade!r})"
        )


def assess_topology(expression: str) -> TopologyResult:
    """Assess the structural topology of a cron expression."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return TopologyResult(
            expression=expression,
            score=0.0,
            grade="disconnected",
            field_scores={},
            error=str(exc),
        )

    names = ["minute", "hour", "dom", "month", "dow"]
    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    scores = {name: _field_constraint(val) for name, val in zip(names, fields)}

    constrained = sum(1 for v in scores.values() if v > 0)
    avg = sum(scores.values()) / len(scores)
    topology_score = round((avg * 0.7) + (constrained / len(scores)) * 0.3, 4)
    return TopologyResult(
        expression=expression,
        score=topology_score,
        grade=_grade(topology_score),
        field_scores=scores,
    )
