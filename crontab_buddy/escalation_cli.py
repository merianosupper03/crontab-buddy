"""CLI commands for escalation policy management."""

from crontab_buddy.escalation import (
    VALID_CHANNELS,
    VALID_LEVELS,
    delete_escalation,
    get_escalation,
    list_escalations,
    set_escalation,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronParseError, CronExpression


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_escalation_set(args) -> None:
    """Set an escalation policy for a cron expression."""
    try:
        set_escalation(
            args.expression,
            args.level,
            args.channel,
            args.contact,
            path=getattr(args, "path", None) or __import__("crontab_buddy.escalation", fromlist=["_DEFAULT_PATH"])._DEFAULT_PATH,
        )
        print(f"Escalation set for '{args.expression}': level={args.level}, channel={args.channel}, contact={args.contact}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_escalation_get(args) -> None:
    """Get the escalation policy for a cron expression."""
    policy = get_escalation(args.expression, path=getattr(args, "path", None) or __import__("crontab_buddy.escalation", fromlist=["_DEFAULT_PATH"])._DEFAULT_PATH)
    if policy is None:
        print(f"No escalation policy found for '{args.expression}'.")
    else:
        desc = _describe(args.expression)
        print(f"Expression : {args.expression}")
        print(f"Description: {desc}")
        print(f"Level      : {policy['level']}")
        print(f"Channel    : {policy['channel']}")
        print(f"Contact    : {policy['contact']}")


def cmd_escalation_delete(args) -> None:
    """Delete the escalation policy for a cron expression."""
    deleted = delete_escalation(args.expression, path=getattr(args, "path", None) or __import__("crontab_buddy.escalation", fromlist=["_DEFAULT_PATH"])._DEFAULT_PATH)
    if deleted:
        print(f"Escalation policy deleted for '{args.expression}'.")
    else:
        print(f"No escalation policy found for '{args.expression}'.")


def cmd_escalation_list(args) -> None:
    """List all escalation policies."""
    policies = list_escalations(path=getattr(args, "path", None) or __import__("crontab_buddy.escalation", fromlist=["_DEFAULT_PATH"])._DEFAULT_PATH)
    if not policies:
        print("No escalation policies defined.")
        return
    for expr, policy in policies.items():
        desc = _describe(expr)
        print(f"  {expr}  [{policy['level']}] via {policy['channel']} -> {policy['contact']}")
        print(f"    {desc}")
