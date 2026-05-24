"""Oscillation analysis for cron expressions.

Measures how regularly a cron expression alternates between active and
inactive periods within an hour. High oscillation means the expression
fires in a back-and-forth pattern; low oscillation means it fires in
a single burst or not at all.
"""

from __future__ import annotations

from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError


def _grade(score: float) -> str:
    if score >= 0.85:
        return "resonant"
    if score >= 0.65:
        return "pulsing"
    if score >= 0.45:
        return "wavering"
    if score >= 0.25:
        return "intermittent"
    if score >= 0.10:
        return "sporadic"
    return "static"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return the list of minutes (0-59) at which the expression fires."""
    field = expr.minute
    if field == "*":
        return list(range(60))
    minutes: List[int] = []
    for part in field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            end = 59 if base == "*" else int(base)
            if "-" in base:
                s, e = base.split("-")
                start, end = int(s), int(e)
            minutes.extend(range(start, end + 1, int(step)))
        elif "-" in part:
            s, e = part.split("-")
            minutes.extend(range(int(s), int(e) + 1))
        else:
            minutes.append(int(part))
    return sorted(set(minutes))


class OscillationResult:
    def __init__(
        self,
        expression: str,
        score: float,
        grade: str,
        transitions: int,
        firing_minutes: int,
        error: Optional[str] = None,
    ) -> None:
        self.expression = expression
        self.score = score
        self.grade = grade
        self.transitions = transitions
        self.firing_minutes = firing_minutes
        self.error = error

    def __str__(self) -> str:
        if self.error:
            return f"OscillationResult({self.expression!r}, error={self.error!r})"
        return (
            f"OscillationResult({self.expression!r}, "
            f"grade={self.grade!r}, score={self.score:.3f}, "
            f"transitions={self.transitions})"
        )


def assess_oscillation(expression: str) -> OscillationResult:
    """Assess the oscillation of a cron expression.

    Oscillation is computed by counting the number of on/off transitions
    within a 60-minute window and normalising by the maximum possible
    transitions (59 for alternating every minute).

    Args:
        expression: A five-field cron expression string.

    Returns:
        An OscillationResult with score, grade, and transition count.
    """
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return OscillationResult(
            expression=expression,
            score=0.0,
            grade="static",
            transitions=0,
            firing_minutes=0,
            error=str(exc),
        )

    minutes = _firing_minutes(expr)
    firing_set = set(minutes)

    # Count transitions between firing and non-firing minutes
    transitions = 0
    prev_active = 0 in firing_set
    for m in range(1, 60):
        active = m in firing_set
        if active != prev_active:
            transitions += 1
        prev_active = active

    max_transitions = 59  # alternating every minute
    score = transitions / max_transitions if max_transitions > 0 else 0.0
    score = min(1.0, score)

    return OscillationResult(
        expression=expression,
        score=round(score, 4),
        grade=_grade(score),
        transitions=transitions,
        firing_minutes=len(minutes),
    )


def batch_oscillation(expressions: List[str]) -> List[OscillationResult]:
    """Assess oscillation for multiple expressions.

    Args:
        expressions: List of cron expression strings.

    Returns:
        List of OscillationResult objects in the same order.
    """
    return [assess_oscillation(e) for e in expressions]
