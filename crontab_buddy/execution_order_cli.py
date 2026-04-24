"""CLI commands for execution order / queue management."""

from __future__ import annotations

from crontab_buddy.execution_order import (
    add_to_queue,
    remove_from_queue,
    get_queue,
    move_up,
    move_down,
    list_queues,
    delete_queue,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_queue_add(args) -> None:
    ok = add_to_queue(args.queue, args.expression, path=args.path)
    if ok:
        print(f"Added '{args.expression}' to queue '{args.queue}'.")
    else:
        print(f"'{args.expression}' is already in queue '{args.queue}'.")


def cmd_queue_remove(args) -> None:
    ok = remove_from_queue(args.queue, args.expression, path=args.path)
    if ok:
        print(f"Removed '{args.expression}' from queue '{args.queue}'.")
    else:
        print(f"'{args.expression}' not found in queue '{args.queue}'.")


def cmd_queue_list(args) -> None:
    entries = get_queue(args.queue, path=args.path)
    if not entries:
        print(f"Queue '{args.queue}' is empty.")
        return
    print(f"Queue '{args.queue}' ({len(entries)} entries):")
    for i, expr in enumerate(entries, 1):
        print(f"  {i}. {expr}  — {_describe(expr)}")


def cmd_queue_move_up(args) -> None:
    ok = move_up(args.queue, args.expression, path=args.path)
    if ok:
        print(f"Moved '{args.expression}' up in queue '{args.queue}'.")
    else:
        print(f"Cannot move up: expression not found or already first.")


def cmd_queue_move_down(args) -> None:
    ok = move_down(args.queue, args.expression, path=args.path)
    if ok:
        print(f"Moved '{args.expression}' down in queue '{args.queue}'.")
    else:
        print(f"Cannot move down: expression not found or already last.")


def cmd_queue_list_all(args) -> None:
    queues = list_queues(path=args.path)
    if not queues:
        print("No queues defined.")
        return
    for q in queues:
        entries = get_queue(q, path=args.path)
        print(f"  {q}: {len(entries)} expression(s)")


def cmd_queue_delete(args) -> None:
    ok = delete_queue(args.queue, path=args.path)
    if ok:
        print(f"Deleted queue '{args.queue}'.")
    else:
        print(f"Queue '{args.queue}' not found.")
