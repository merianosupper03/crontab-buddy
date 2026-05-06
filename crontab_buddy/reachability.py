"""Reachability analysis: determine if a cron expression can ever fire
within a given date range, or if it is effectively unreachable."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .parser import CronExpression, CronParseError
from .scheduler import next_runs


@dataclass
class ReachabilityResult:
    expression: str
    reachable: bool
    reason: str
    next_occurrences: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.reachable

    def __str__(self) -> str:
        status = "REACHABLE" if self.reachable else "UNREACHABLE"
        lines = [f"{self.expression}  [{status}]", f"  Reason : {self.reason}"]
        if self.next_occurrences:
            lines.append("  Next   : " + ", ".join(self.next_occurrences[:3]))
        if self.error:
            lines.append(f"  Error  : {self.error}")
        return "\n".join(lines)


def check_reachability(
    expression: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    window_days: int = 366,
) -> ReachabilityResult:
    """Check whether *expression* fires at least once between *start* and *end*.

    If *start*/*end* are omitted a rolling window of *window_days* is used.
    """
    if start is None:
        start = datetime.utcnow()
    if end is None:
        end = start + timedelta(days=window_days)

    try:
        CronExpression(expression)
    except CronParseError as exc:
        return ReachabilityResult(
            expression=expression,
            reachable=False,
            reason="invalid expression",
            error=str(exc),
        )

    runs = next_runs(expression, count=5, after=start)
    hits = [r for r in runs if start <= r <= end]

    if hits:
        formatted = [r.strftime("%Y-%m-%d %H:%M") for r in hits]
        return ReachabilityResult(
            expression=expression,
            reachable=True,
            reason=f"fires {len(hits)} time(s) in window",
            next_occurrences=formatted,
        )

    return ReachabilityResult(
        expression=expression,
        reachable=False,
        reason=f"no occurrences between {start.date()} and {end.date()}",
    )


def batch_reachability(
    expressions: List[str],
    window_days: int = 366,
) -> List[ReachabilityResult]:
    """Run reachability checks on a list of expressions."""
    return [check_reachability(expr, window_days=window_days) for expr in expressions]
