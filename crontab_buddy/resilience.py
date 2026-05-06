"""Resilience scoring for cron expressions.

Scores how resilient a cron expression is based on factors like
frequency, retry config, healthcheck, timeout, and lock settings.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResilienceResult:
    expression: str
    score: int  # 0-100
    grade: str
    factors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Score      : {self.score}/100 (Grade: {self.grade})",
        ]
        if self.factors:
            lines.append("Factors    : " + ", ".join(self.factors))
        if self.suggestions:
            lines.append("Suggestions:")
            for s in self.suggestions:
                lines.append(f"  - {s}")
        return "\n".join(lines)


def _grade(score: int) -> str:
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"


def score_resilience(
    expression: str,
    has_retry: bool = False,
    has_healthcheck: bool = False,
    has_timeout: bool = False,
    has_lock: bool = False,
    has_notify: bool = False,
    is_high_frequency: Optional[bool] = None,
) -> ResilienceResult:
    score = 20  # baseline
    factors: List[str] = []
    suggestions: List[str] = []

    if has_retry:
        score += 20
        factors.append("retry configured")
    else:
        suggestions.append("Add a retry policy to handle transient failures")

    if has_healthcheck:
        score += 20
        factors.append("healthcheck enabled")
    else:
        suggestions.append("Set up a healthcheck endpoint for monitoring")

    if has_timeout:
        score += 15
        factors.append("timeout set")
    else:
        suggestions.append("Define a timeout to prevent runaway jobs")

    if has_lock:
        score += 15
        factors.append("lock in place")
    else:
        suggestions.append("Use a lock to avoid overlapping executions")

    if has_notify:
        score += 10
        factors.append("notifications active")
    else:
        suggestions.append("Enable notifications for failure alerting")

    if is_high_frequency:
        score = max(0, score - 10)
        factors.append("high-frequency penalty applied")

    score = min(score, 100)
    return ResilienceResult(
        expression=expression,
        score=score,
        grade=_grade(score),
        factors=factors,
        suggestions=suggestions,
    )
