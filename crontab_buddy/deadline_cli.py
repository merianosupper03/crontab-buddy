"""CLI commands for deadline management."""
from __future__ import annotations

from datetime import datetime
from crontab_buddy.deadline import set_deadline, get_deadline, delete_deadline, list_deadlines, is_overdue
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_deadline_set(args) -> None:
    try:
        set_deadline(args.expression, args.deadline, getattr(args, "note", ""), path=args.path)
        print(f"Deadline set: {args.expression} → {args.deadline}")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_deadline_get(args) -> None:
    info = get_deadline(args.expression, path=args.path)
    if info is None:
        print(f"No deadline set for: {args.expression}")
        return
    overdue = is_overdue(args.expression, path=args.path)
    status = "OVERDUE" if overdue else "upcoming"
    print(f"Expression : {args.expression}")
    print(f"Description: {_describe(args.expression)}")
    print(f"Deadline   : {info['deadline']} [{status}]")
    if info.get("note"):
        print(f"Note       : {info['note']}")


def cmd_deadline_delete(args) -> None:
    removed = delete_deadline(args.expression, path=args.path)
    if removed:
        print(f"Deadline removed for: {args.expression}")
    else:
        print(f"No deadline found for: {args.expression}")


def cmd_deadline_list(args) -> None:
    entries = list_deadlines(path=args.path)
    if not entries:
        print("No deadlines set.")
        return
    now = datetime.now()
    for entry in entries:
        dt = datetime.fromisoformat(entry["deadline"])
        flag = " [OVERDUE]" if dt < now else ""
        desc = _describe(entry["expression"])
        print(f"{entry['deadline']}{flag}  {entry['expression']}  — {desc}")
        if entry.get("note"):
            print(f"  note: {entry['note']}")
