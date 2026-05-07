"""Coherence scoring: measures how internally consistent a cron expression is."""

from dataclasses import dataclass
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class CoherenceResult:
    expression: str
    score: float  # 0.0 - 1.0
    grade: str
    notes: list

    def __str__(self):
        note_str = "; ".join(self.notes) if self.notes else "no issues"
        return f"[{self.grade}] {self.expression} (score={self.score:.2f}) — {note_str}"


def _grade(score: float) -> str:
    if score >= 0.9:
        return "excellent"
    if score >= 0.7:
        return "good"
    if score >= 0.5:
        return "fair"
    if score >= 0.3:
        return "poor"
    return "incoherent"


def assess_coherence(expression: str) -> CoherenceResult:
    """Assess how coherent/consistent a cron expression is."""
    notes = []
    deductions = 0.0

    try:
        expr = CronExpression(expression)
    except CronParseError as e:
        return CoherenceResult(
            expression=expression,
            score=0.0,
            grade="incoherent",
            notes=[f"parse error: {e}"],
        )

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    names = ["minute", "hour", "dom", "month", "dow"]

    # Penalise if both dom and dow are non-wildcard (ambiguous semantics)
    if expr.dom != "*" and expr.dow != "*":
        notes.append("both dom and dow are set — behaviour is OR, not AND")
        deductions += 0.2

    # Penalise step-of-1 (redundant, e.g. */1)
    for name, field in zip(names, fields):
        if "/1" in field:
            notes.append(f"{name} uses redundant step /1")
            deductions += 0.1

    # Penalise ranges where start > end (e.g. 50-10)
    for name, field in zip(names, fields):
        if "-" in field and "/" not in field and "," not in field:
            parts = field.split("-")
            try:
                lo, hi = int(parts[0]), int(parts[1])
                if lo > hi:
                    notes.append(f"{name} has inverted range {field}")
                    deductions += 0.25
            except (ValueError, IndexError):
                pass

    # Penalise list with a single item (e.g. 5,5 or just one value in a list)
    for name, field in zip(names, fields):
        if "," in field:
            items = field.split(",")
            if len(set(items)) == 1:
                notes.append(f"{name} list has duplicate/single unique value")
                deductions += 0.1

    score = max(0.0, round(1.0 - deductions, 4))
    return CoherenceResult(
        expression=expression,
        score=score,
        grade=_grade(score),
        notes=notes,
    )
