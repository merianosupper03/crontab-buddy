"""Scatter: measure how spread out firing times are across the hour."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.9:
        return "diffuse"
    if score >= 0.7:
        return "spread"
    if score >= 0.5:
        return "moderate"
    if score >= 0.3:
        return "clustered"
    return "concentrated"


def _firing_minutes(expr: CronExpression) -> List[int]:
    m = expr.minute
    if m == "*":
        return list(range(60))
    if "/" in m:
        parts = m.split("/")
        start = 0 if parts[0] == "*" else int(parts[0])
        step = int(parts[1])
        return list(range(start, 60, step))
    if "-" in m:
        lo, hi = m.split("-")
        return list(range(int(lo), int(hi) + 1))
    if "," in m:
        return [int(x) for x in m.split(",")]
    return [int(m)]


@dataclass
class ScatterResult:
    expression: str
    score: float
    grade: str
    firing_minutes: List[int]
    spread: float
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"Scatter({self.expression}): error={self.error}"
        return (
            f"Scatter({self.expression}): grade={self.grade} "
            f"score={self.score:.3f} spread={self.spread:.1f}min"
        )


def assess_scatter(expression: str) -> ScatterResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ScatterResult(
            expression=expression,
            score=0.0,
            grade="concentrated",
            firing_minutes=[],
            spread=0.0,
            error=str(exc),
        )

    minutes = _firing_minutes(expr)
    if len(minutes) <= 1:
        spread = 0.0
        score = 0.0
    else:
        spread = float(max(minutes) - min(minutes))
        score = min(spread / 59.0, 1.0)
        if len(minutes) > 2:
            gaps = [minutes[i + 1] - minutes[i] for i in range(len(minutes) - 1)]
            mean_gap = sum(gaps) / len(gaps)
            variance = sum((g - mean_gap) ** 2 for g in gaps) / len(gaps)
            uniformity = 1.0 / (1.0 + variance / max(mean_gap, 1))
            score = round((score + uniformity) / 2.0, 4)
        else:
            score = round(score, 4)

    return ScatterResult(
        expression=expression,
        score=score,
        grade=_grade(score),
        firing_minutes=minutes,
        spread=spread,
    )


def batch_scatter(expressions: List[str]) -> List[ScatterResult]:
    return [assess_scatter(e) for e in expressions]
