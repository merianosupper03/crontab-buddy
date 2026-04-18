"""Compare two cron expressions and describe what changed."""

from typing import List
from crontab_buddy.parser import CronExpression

FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]


def diff_expressions(expr_a: str, expr_b: str) -> List[str]:
    """Return a list of human-readable change descriptions between two expressions."""
    a = CronExpression(expr_a)
    b = CronExpression(expr_b)

    fields_a = [a.minute, a.hour, a.dom, a.month, a.dow]
    fields_b = [b.minute, b.hour, b.dom, b.month, b.dow]

    changes = []
    for name, fa, fb in zip(FIELD_NAMES, fields_a, fields_b):
        if fa != fb:
            changes.append(f"{name}: '{fa}' -> '{fb}'")

    return changes


def expressions_equal(expr_a: str, expr_b: str) -> bool:
    """Return True if both expressions are semantically identical."""
    return diff_expressions(expr_a, expr_b) == []
