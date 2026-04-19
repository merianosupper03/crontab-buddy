"""CLI commands for pinned expressions."""
from crontab_buddy.pin import pin_expression, unpin_expression, get_pins, is_pinned, clear_pins
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except CronParseError:
        return "(invalid expression)"


def cmd_pin_add(args, path=None):
    kwargs = {"path": path} if path else {}
    if pin_expression(args.expression, **kwargs):
        print(f"Pinned: {args.expression}")
    else:
        print(f"Already pinned: {args.expression}")


def cmd_pin_remove(args, path=None):
    kwargs = {"path": path} if path else {}
    if unpin_expression(args.expression, **kwargs):
        print(f"Unpinned: {args.expression}")
    else:
        print(f"Not found in pins: {args.expression}")


def cmd_pin_list(args, path=None):
    kwargs = {"path": path} if path else {}
    pins = get_pins(**kwargs)
    if not pins:
        print("No pinned expressions.")
        return
    for expr in pins:
        print(f"  {expr}  —  {_describe(expr)}")


def cmd_pin_check(args, path=None):
    kwargs = {"path": path} if path else {}
    if is_pinned(args.expression, **kwargs):
        print(f"Pinned: {args.expression}")
    else:
        print(f"Not pinned: {args.expression}")


def cmd_pin_clear(args, path=None):
    kwargs = {"path": path} if path else {}
    clear_pins(**kwargs)
    print("All pins cleared.")
