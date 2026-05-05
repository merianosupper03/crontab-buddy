"""Drift detection: compare expected vs actual run times for a cron expression."""

from datetime import datetime, timedelta
from typing import List, Optional
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.scheduler import next_runs


class DriftResult:
    def __init__(self, expression: str, expected: datetime, actual: datetime):
        self.expression = expression
        self.expected = expected
        self.actual = actual
        self.delta_seconds = (actual - expected).total_seconds()

    @property
    def drifted(self) -> bool:
        return abs(self.delta_seconds) > 0

    def __str__(self) -> str:
        direction = "late" if self.delta_seconds > 0 else "early"
        secs = abs(self.delta_seconds)
        if not self.drifted:
            return f"{self.expression}: no drift detected"
        return (
            f"{self.expression}: {direction} by {secs:.0f}s "
            f"(expected {self.expected.isoformat()}, got {self.actual.isoformat()})"
        )


def detect_drift(
    expression: str,
    actual_run: datetime,
    reference: Optional[datetime] = None,
) -> DriftResult:
    """Detect drift between an actual run time and the nearest expected run."""
    try:
        CronExpression(expression)
    except CronParseError as exc:
        raise ValueError(f"Invalid expression: {exc}") from exc

    base = reference or (actual_run - timedelta(hours=1))
    upcoming = next_runs(expression, count=10, start=base)

    if not upcoming:
        raise ValueError("Could not compute expected runs for expression.")

    closest = min(upcoming, key=lambda dt: abs((dt - actual_run).total_seconds()))
    return DriftResult(expression=expression, expected=closest, actual=actual_run)


def drift_summary(results: List[DriftResult]) -> dict:
    """Summarise a list of DriftResult objects."""
    drifted = [r for r in results if r.drifted]
    deltas = [abs(r.delta_seconds) for r in drifted]
    return {
        "total": len(results),
        "drifted": len(drifted),
        "max_drift_seconds": max(deltas) if deltas else 0,
        "avg_drift_seconds": sum(deltas) / len(deltas) if deltas else 0,
    }
