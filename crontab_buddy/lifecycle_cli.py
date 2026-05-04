"""CLI commands for lifecycle management."""

from __future__ import annotations

from crontab_buddy.lifecycle import (
    VALID_STATES,
    delete_lifecycle,
    get_lifecycle,
    list_all_lifecycles,
    list_by_state,
    set_lifecycle,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except (CronParseError, Exception):
        return "(invalid expression)"


def cmd_lifecycle_set(args) -> None:
    try:
        set_lifecycle(args.expression, args.state, getattr(args, "reason", None))
        print(f"Lifecycle set: '{args.expression}' -> {args.state}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_lifecycle_get(args) -> None:
    info = get_lifecycle(args.expression)
    if info is None:
        print(f"No lifecycle info for '{args.expression}'.")
        return
    print(f"Expression : {args.expression}")
    print(f"Description: {_describe(args.expression)}")
    print(f"State      : {info['state']}")
    if info.get("previous_state"):
        print(f"Previous   : {info['previous_state']}")
    if info.get("reason"):
        print(f"Reason     : {info['reason']}")
    print(f"Updated    : {info['updated_at']}")


def cmd_lifecycle_delete(args) -> None:
    if delete_lifecycle(args.expression):
        print(f"Lifecycle info removed for '{args.expression}'.")
    else:
        print(f"No lifecycle info found for '{args.expression}'.")


def cmd_lifecycle_list(args) -> None:
    state_filter = getattr(args, "state", None)
    try:
        entries = list_by_state(state_filter) if state_filter else list_all_lifecycles()
    except ValueError as e:
        print(f"Error: {e}")
        return
    if not entries:
        print("No lifecycle entries found.")
        return
    for entry in entries:
        desc = _describe(entry["expression"])
        print(f"[{entry['state'].upper()}] {entry['expression']} — {desc}")
        if entry.get("reason"):
            print(f"  Reason: {entry['reason']}")
