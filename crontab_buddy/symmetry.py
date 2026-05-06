"""Symmetry analysis: detect if two cron expressions are semantically equivalent
or mirror each other in a meaningful way."""

from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


class SymmetryResult:
    def __init__(self, expr_a: str, expr_b: str, symmetric: bool, reason: str):
        self.expr_a = expr_a
        self.expr_b = expr_b
        self.symmetric = symmetric
        self.reason = reason

    def __bool__(self) -> bool:
        return self.symmetric

    def __str__(self) -> str:
        status = "symmetric" if self.symmetric else "not symmetric"
        return f"{self.expr_a!r} vs {self.expr_b!r}: {status} — {self.reason}"


def _parse_safe(expr: str) -> Optional[CronExpression]:
    try:
        return CronExpression(expr)
    except (CronParseError, ValueError):
        return None


def _fields_equal(a: CronExpression, b: CronExpression) -> list[str]:
    """Return list of field names where the two expressions differ."""
    names = ["minute", "hour", "dom", "month", "dow"]
    attrs = ["minute", "hour", "dom", "month", "dow"]
    return [names[i] for i, attr in enumerate(attrs) if getattr(a, attr) != getattr(b, attr)]


def check_symmetry(expr_a: str, expr_b: str) -> SymmetryResult:
    """Check whether two cron expressions are semantically symmetric (identical fields)."""
    a = _parse_safe(expr_a)
    b = _parse_safe(expr_b)

    if a is None:
        return SymmetryResult(expr_a, expr_b, False, f"invalid expression: {expr_a!r}")
    if b is None:
        return SymmetryResult(expr_a, expr_b, False, f"invalid expression: {expr_b!r}")

    diffs = _fields_equal(a, b)
    if not diffs:
        return SymmetryResult(expr_a, expr_b, True, "all fields match")

    diff_str = ", ".join(diffs)
    return SymmetryResult(expr_a, expr_b, False, f"fields differ: {diff_str}")


def batch_symmetry(expressions: list[str]) -> list[SymmetryResult]:
    """Compare each consecutive pair in a list of expressions."""
    results = []
    for i in range(len(expressions) - 1):
        results.append(check_symmetry(expressions[i], expressions[i + 1]))
    return results
