"""Gradient analysis: measure how smoothly a cron expression distributes load over time."""

from dataclasses import dataclass, field
from typing import List, Optional
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class GradientResult:
    expression: str
    score: float  # 0.0 (abrupt/spiky) to 1.0 (smooth/gradual)
    label: str
    deltas: List[int]  # minute-level gaps between firings in a 60-min window
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"Gradient({self.expression!r}): error — {self.error}"
        return f"Gradient({self.expression!r}): {self.label} ({self.score:.2f})"


def _grade(score: float) -> str:
    if score >= 0.85:
        return "smooth"
    if score >= 0.60:
        return "gradual"
    if score >= 0.35:
        return "uneven"
    return "spiky"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return sorted list of minutes (0-59) when the expression fires within hour 0."""
    minute_field = expr.fields[0]
    minutes = []
    for m in range(60):
        from crontab_buddy.scheduler import _matches_field
        if _matches_field(minute_field, m, 0, 59):
            minutes.append(m)
    return sorted(minutes)


def compute_gradient(expression: str) -> GradientResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as e:
        return GradientResult(expression=expression, score=0.0, label="spiky", deltas=[], error=str(e))

    firings = _firing_minutes(expr)
    if len(firings) < 2:
        score = 0.0
        deltas = []
    else:
        gaps = [firings[i + 1] - firings[i] for i in range(len(firings) - 1)]
        mean_gap = sum(gaps) / len(gaps)
        variance = sum((g - mean_gap) ** 2 for g in gaps) / len(gaps)
        # Normalise: lower variance relative to mean = smoother
        cv = (variance ** 0.5) / mean_gap if mean_gap > 0 else 1.0
        score = max(0.0, min(1.0, 1.0 / (1.0 + cv)))
        deltas = gaps

    label = _grade(score)
    return GradientResult(expression=expression, score=round(score, 4), label=label, deltas=deltas)
