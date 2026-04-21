"""CLI commands for managing cron expression cooldowns."""

from crontab_buddy.cooldown import (
    set_cooldown,
    get_cooldown,
    delete_cooldown,
    list_cooldowns,
    VALID_UNITS,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except (CronParseError, Exception):
        return "(invalid expression)"


def cmd_cooldown_set(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    try:
        set_cooldown(args.expression, args.amount, args.unit, **kwargs)
        print(f"Cooldown set: '{args.expression}' -> {args.amount} {args.unit}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_cooldown_get(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    result = get_cooldown(args.expression, **kwargs)
    if result is None:
        print(f"No cooldown set for '{args.expression}'.")
    else:
        desc = _describe(args.expression)
        print(f"Expression : {args.expression}")
        print(f"Description: {desc}")
        print(f"Cooldown   : {result['amount']} {result['unit']}")


def cmd_cooldown_delete(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    removed = delete_cooldown(args.expression, **kwargs)
    if removed:
        print(f"Cooldown removed for '{args.expression}'.")
    else:
        print(f"No cooldown found for '{args.expression}'.")


def cmd_cooldown_list(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    entries = list_cooldowns(**kwargs)
    if not entries:
        print("No cooldowns configured.")
        return
    for expr, cfg in entries.items():
        desc = _describe(expr)
        print(f"{expr} | {cfg['amount']} {cfg['unit']} | {desc}")
