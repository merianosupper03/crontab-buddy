"""Detect overlapping or conflicting cron expressions."""

from dataclasses import dataclass, field
from typing import List, Tuple
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.scheduler import next_runs
from datetime import datetime


@dataclass
class OverlapResult:
    expr_a: str
    expr_b: str
    overlapping_times: List[datetime] = field(default_factory=list)
    error: str = ""

    def __bool__(self) -> bool:
        return len(self.overlapping_times) > 0

    def __str__(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.overlapping_times:
            return f"No overlap between '{self.expr_a}' and '{self.expr_b}'"
        count = len(self.overlapping_times)
        first = self.overlapping_times[0].strftime("%Y-%m-%d %H:%M")
        return (
            f"'{self.expr_a}' and '{self.expr_b}' overlap {count} time(s) "
            f"in the next 24h (first: {first})"
        )


def _safe_parse(expr: str):
    try:
        return CronExpression(expr)
    except CronParseError:
        return None


def detect_overlap(
    expr_a: str,
    expr_b: str,
    reference: datetime = None,
    hours: int = 24,
    max_runs: int = 100,
) -> OverlapResult:
    """Find times when both expressions fire within the same minute."""
    if reference is None:
        reference = datetime.now().replace(second=0, microsecond=0)

    parsed_a = _safe_parse(expr_a)
    if parsed_a is None:
        return OverlapResult(expr_a, expr_b, error=f"Invalid expression: {expr_a}")

    parsed_b = _safe_parse(expr_b)
    if parsed_b is None:
        return OverlapResult(expr_a, expr_b, error=f"Invalid expression: {expr_b}")

    runs_a = set(next_runs(parsed_a, reference, count=max_runs))
    runs_b = set(next_runs(parsed_b, reference, count=max_runs))

    from datetime import timedelta
    cutoff = reference + timedelta(hours=hours)
    overlap = sorted(
        dt for dt in runs_a & runs_b if dt < cutoff
    )

    return OverlapResult(expr_a, expr_b, overlapping_times=overlap)


def find_all_overlaps(
    expressions: List[str],
    reference: datetime = None,
    hours: int = 24,
) -> List[OverlapResult]:
    """Check all pairs of expressions for overlaps."""
    results = []
    for i, a in enumerate(expressions):
        for b in expressions[i + 1:]:
            result = detect_overlap(a, b, reference=reference, hours=hours)
            if result or result.error:
                results.append(result)
    return results
