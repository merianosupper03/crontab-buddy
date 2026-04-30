"""CLI commands for SLA management."""

from __future__ import annotations

from crontab_buddy.sla import (
    VALID_POLICIES,
    check_sla,
    delete_sla,
    get_sla,
    list_slas,
    set_sla,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_sla_set(args) -> None:
    """Set an SLA for a cron expression."""
    try:
        entry = set_sla(
            args.expression,
            int(args.max_seconds),
            policy=getattr(args, "policy", "strict") or "strict",
            note=getattr(args, "note", None),
        )
        print(f"SLA set for '{args.expression}': max {entry['max_duration_seconds']}s, policy={entry['policy']}")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_sla_get(args) -> None:
    """Get the SLA for a cron expression."""
    entry = get_sla(args.expression)
    if entry is None:
        print(f"No SLA found for '{args.expression}'")
        return
    print(f"Expression : {args.expression}")
    print(f"Description: {_describe(args.expression)}")
    print(f"Max seconds: {entry['max_duration_seconds']}")
    print(f"Policy     : {entry['policy']}")
    if entry.get("note"):
        print(f"Note       : {entry['note']}")


def cmd_sla_delete(args) -> None:
    """Delete the SLA for a cron expression."""
    if delete_sla(args.expression):
        print(f"SLA deleted for '{args.expression}'")
    else:
        print(f"No SLA found for '{args.expression}'")


def cmd_sla_check(args) -> None:
    """Check whether a run duration violated the SLA."""
    result = check_sla(args.expression, int(args.actual_seconds))
    if result["status"] == "no_sla":
        print(f"No SLA configured for '{args.expression}'")
        return
    status_label = "VIOLATED" if result["violated"] else "OK"
    print(f"[{status_label}] '{args.expression}' ran in {result['actual_seconds']}s (max {result['max_duration_seconds']}s, policy={result['policy']})")


def cmd_sla_list(args) -> None:
    """List all SLA entries."""
    entries = list_slas()
    if not entries:
        print("No SLAs configured.")
        return
    for expr, entry in entries.items():
        note = f" | {entry['note']}" if entry.get("note") else ""
        print(f"{expr}  [{entry['policy']}]  max={entry['max_duration_seconds']}s{note}")
