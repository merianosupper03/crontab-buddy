"""CLI commands for quota management."""

from crontab_buddy.quota import (
    set_quota,
    get_quota,
    delete_quota,
    list_quotas,
    VALID_PERIODS,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_quota_set(args) -> None:
    """Set a quota for an expression."""
    try:
        set_quota(args.expression, args.max_runs, args.period)
        print(f"Quota set: {args.expression!r} — max {args.max_runs} runs per {args.period}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_quota_get(args) -> None:
    """Get the quota for an expression."""
    quota = get_quota(args.expression)
    if quota is None:
        print(f"No quota set for: {args.expression!r}")
    else:
        desc = _describe(args.expression)
        print(f"Expression : {args.expression}")
        print(f"Description: {desc}")
        print(f"Max runs   : {quota['max_runs']} per {quota['period']}")


def cmd_quota_delete(args) -> None:
    """Delete the quota for an expression."""
    if delete_quota(args.expression):
        print(f"Quota removed for: {args.expression!r}")
    else:
        print(f"No quota found for: {args.expression!r}")


def cmd_quota_list(args) -> None:
    """List all quota entries."""
    quotas = list_quotas()
    if not quotas:
        print("No quotas defined.")
        return
    for expr, cfg in quotas.items():
        desc = _describe(expr)
        print(f"{expr}  [{cfg['max_runs']}/{cfg['period']}]  — {desc}")
