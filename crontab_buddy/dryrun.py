"""Dry-run simulation: show what would happen if a cron expression fired now."""

from datetime import datetime, timezone
from typing import Optional

from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.humanizer import humanize
from crontab_buddy.scheduler import next_runs


class DryRunResult:
    def __init__(self, expression: str, description: str, would_fire_now: bool,
                 next_occurrence: Optional[datetime], error: Optional[str] = None):
        self.expression = expression
        self.description = description
        self.would_fire_now = would_fire_now
        self.next_occurrence = next_occurrence
        self.error = error

    def __str__(self) -> str:
        if self.error:
            return f"[error] {self.error}"
        status = "WOULD FIRE" if self.would_fire_now else "would not fire"
        next_str = self.next_occurrence.strftime("%Y-%m-%d %H:%M") if self.next_occurrence else "N/A"
        return (
            f"Expression : {self.expression}\n"
            f"Description: {self.description}\n"
            f"Status now : {status}\n"
            f"Next run   : {next_str}"
        )


def dry_run(expression: str, at: Optional[datetime] = None) -> DryRunResult:
    """Simulate whether the expression would fire at the given time (default: now)."""
    if at is None:
        at = datetime.now(timezone.utc).replace(second=0, microsecond=0)

    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return DryRunResult(expression, "", False, None, error=str(exc))

    description = humanize(expr)

    # Check if it would fire at the exact given minute
    from crontab_buddy.scheduler import _matches_field
    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    values = [at.minute, at.hour, at.day, at.month, at.weekday()]
    # cron dow: 0=Sunday; Python weekday: 0=Monday — normalise
    cron_dow = (at.weekday() + 1) % 7  # Mon->1 ... Sun->0
    values[4] = cron_dow

    would_fire = all(_matches_field(f, v) for f, v in zip(fields, values))

    runs = next_runs(expression, start=at, count=1)
    next_occ = runs[0] if runs else None

    return DryRunResult(expression, description, would_fire, next_occ)


def format_dry_run_json(result: DryRunResult) -> dict:
    return {
        "expression": result.expression,
        "description": result.description,
        "would_fire_now": result.would_fire_now,
        "next_occurrence": result.next_occurrence.isoformat() if result.next_occurrence else None,
        "error": result.error,
    }
