"""CLI commands for managing throttle settings."""

from crontab_buddy.throttle import (
    set_throttle,
    get_throttle,
    delete_throttle,
    list_throttles,
    VALID_UNITS,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_throttle_set(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    if args.unit not in VALID_UNITS:
        print(f"Error: unit must be one of {VALID_UNITS}")
        return
    try:
        interval = int(args.interval)
    except (ValueError, TypeError):
        print("Error: interval must be an integer")
        return
    try:
        set_throttle(args.expression, interval, args.unit, **kwargs)
        print(f"Throttle set: {args.expression} — every {interval} {args.unit}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_throttle_get(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    result = get_throttle(args.expression, **kwargs)
    if result is None:
        print(f"No throttle set for: {args.expression}")
    else:
        desc = _describe(args.expression)
        print(f"{args.expression} ({desc})")
        print(f"  Throttle: every {result['interval']} {result['unit']}")


def cmd_throttle_delete(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    removed = delete_throttle(args.expression, **kwargs)
    if removed:
        print(f"Throttle removed for: {args.expression}")
    else:
        print(f"No throttle found for: {args.expression}")


def cmd_throttle_list(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    all_throttles = list_throttles(**kwargs)
    if not all_throttles:
        print("No throttles configured.")
        return
    for expr, cfg in all_throttles.items():
        desc = _describe(expr)
        print(f"{expr} ({desc}) — every {cfg['interval']} {cfg['unit']}")
