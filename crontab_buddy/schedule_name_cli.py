"""CLI commands for named schedules."""

from crontab_buddy.schedule_name import save_schedule, get_schedule, delete_schedule, list_schedules
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_schedule_save(args, path=None):
    kwargs = {"path": path} if path else {}
    save_schedule(args.name, args.expression, getattr(args, "description", ""), **kwargs)
    print(f"Saved schedule '{args.name}': {args.expression}")


def cmd_schedule_get(args, path=None):
    kwargs = {"path": path} if path else {}
    entry = get_schedule(args.name, **kwargs)
    if entry is None:
        print(f"No schedule named '{args.name}'.")
        return
    expr = entry["expression"]
    desc = entry.get("description", "")
    print(f"Name       : {args.name}")
    print(f"Expression : {expr}")
    print(f"Readable   : {_describe(expr)}")
    if desc:
        print(f"Description: {desc}")


def cmd_schedule_delete(args, path=None):
    kwargs = {"path": path} if path else {}
    removed = delete_schedule(args.name, **kwargs)
    if removed:
        print(f"Deleted schedule '{args.name}'.")
    else:
        print(f"No schedule named '{args.name}' found.")


def cmd_schedule_list(args, path=None):
    kwargs = {"path": path} if path else {}
    schedules = list_schedules(**kwargs)
    if not schedules:
        print("No named schedules saved.")
        return
    for name, entry in schedules.items():
        expr = entry["expression"]
        print(f"  {name:20s} {expr:25s} {_describe(expr)}")
