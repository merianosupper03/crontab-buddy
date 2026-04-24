"""CLI commands for rollback management."""

from __future__ import annotations

from crontab_buddy.rollback import (
    push_rollback,
    pop_rollback,
    peek_rollback,
    get_rollback_stack,
    clear_rollback,
    list_rollback_slots,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_rollback_push(args) -> None:
    push_rollback(args.name, args.expression, path=args.path)
    print(f"Pushed '{args.expression}' onto rollback stack '{args.name}'.")


def cmd_rollback_pop(args) -> None:
    expr = pop_rollback(args.name, path=args.path)
    if expr is None:
        print(f"Rollback stack '{args.name}' is empty.")
    else:
        print(f"Rolled back to: {expr}")
        print(f"  {_describe(expr)}")


def cmd_rollback_peek(args) -> None:
    expr = peek_rollback(args.name, path=args.path)
    if expr is None:
        print(f"Rollback stack '{args.name}' is empty.")
    else:
        print(f"Current top: {expr}")
        print(f"  {_describe(expr)}")


def cmd_rollback_list(args) -> None:
    stack = get_rollback_stack(args.name, path=args.path)
    if not stack:
        print(f"No rollback entries for '{args.name}'.")
        return
    print(f"Rollback stack for '{args.name}' ({len(stack)} entries):")
    for i, entry in enumerate(reversed(stack), 1):
        desc = _describe(entry["expression"])
        print(f"  [{i}] {entry['expression']}  —  {desc}  (saved {entry['timestamp']})")


def cmd_rollback_clear(args) -> None:
    removed = clear_rollback(args.name, path=args.path)
    if removed:
        print(f"Cleared rollback stack '{args.name}'.")
    else:
        print(f"No rollback stack found for '{args.name}'.")


def cmd_rollback_slots(args) -> None:
    slots = list_rollback_slots(path=args.path)
    if not slots:
        print("No rollback slots found.")
    else:
        print("Rollback slots:")
        for s in slots:
            print(f"  {s}")
