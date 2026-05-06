"""Alignment analysis: how well a cron expression aligns to common scheduling patterns."""

from dataclasses import dataclass
from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


ALIGNMENT_PATTERNS = [
    ("exact minute", lambda e: e.minute != "*" and "/" not in e.minute and "," not in e.minute),
    ("exact hour", lambda e: e.hour != "*" and "/" not in e.hour and "," not in e.hour),
    ("midnight anchor", lambda e: e.hour == "0" and e.minute == "0"),
    ("top of hour", lambda e: e.minute == "0" and e.hour == "*"),
    ("wildcard dom", lambda e: e.dom == "*"),
    ("wildcard dow", lambda e: e.dow == "*"),
    ("specific dow", lambda e: e.dow != "*" and e.dom == "*"),
    ("specific dom", lambda e: e.dom != "*" and e.dow == "*"),
]


@dataclass
class AlignmentResult:
    expression: str
    score: float
    grade: str
    matched_patterns: list
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"AlignmentResult(error={self.error})"
        patterns = ", ".join(self.matched_patterns) if self.matched_patterns else "none"
        return (
            f"AlignmentResult(expression={self.expression!r}, "
            f"score={self.score:.2f}, grade={self.grade}, patterns=[{patterns}])"
        )


def _grade(score: float) -> str:
    if score >= 0.75:
        return "well-aligned"
    if score >= 0.5:
        return "aligned"
    if score >= 0.25:
        return "loosely-aligned"
    return "unaligned"


def assess_alignment(expression: str) -> AlignmentResult:
    """Assess how well a cron expression aligns to common scheduling patterns."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return AlignmentResult(
            expression=expression,
            score=0.0,
            grade="unaligned",
            matched_patterns=[],
            error=str(exc),
        )

    matched = [name for name, check in ALIGNMENT_PATTERNS if check(expr)]
    score = round(len(matched) / len(ALIGNMENT_PATTERNS), 4)
    return AlignmentResult(
        expression=expression,
        score=score,
        grade=_grade(score),
        matched_patterns=matched,
    )
