"""CLI commands for managing trigger rules on cron expressions."""

from crontab_buddy.trigger import (
    VALID_EVENTS,
    set_trigger,
    get_trigger,
    delete_trigger,
    list_triggers,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_trigger_set(args) -> None:
    """Set a trigger rule for a cron expression."""
    try:
        set_trigger(
            args.expression,
            args.event,
            condition=getattr(args, "condition", None),
            path=args.path,
        )
        print(f"Trigger set: '{args.expression}' on event '{args.event}'")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_trigger_get(args) -> None:
    """Get the trigger rule for a cron expression."""
    rule = get_trigger(args.expression, path=args.path)
    if rule is None:
        print(f"No trigger found for '{args.expression}'.")
    else:
        desc = _describe(args.expression)
        print(f"Expression : {args.expression}")
        print(f"Description: {desc}")
        print(f"Event      : {rule['event']}")
        if rule.get("condition"):
            print(f"Condition  : {rule['condition']}")


def cmd_trigger_delete(args) -> None:
    """Delete the trigger rule for a cron expression."""
    removed = delete_trigger(args.expression, path=args.path)
    if removed:
        print(f"Trigger removed for '{args.expression}'.")
    else:
        print(f"No trigger found for '{args.expression}'.")


def cmd_trigger_list(args) -> None:
    """List all trigger rules."""
    rules = list_triggers(path=args.path)
    if not rules:
        print("No triggers stored.")
        return
    for rule in rules:
        cond = f" | condition: {rule['condition']}" if rule.get("condition") else ""
        print(f"{rule['expression']}  ->  {rule['event']}{cond}")
