"""CLI commands for managing concurrency policies."""
from __future__ import annotations

from crontab_buddy.concurrency import (
    VALID_POLICIES,
    delete_concurrency,
    get_concurrency,
    list_concurrency,
    set_concurrency,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except (CronParseError, Exception):
        return "(invalid expression)"


def cmd_concurrency_set(args) -> None:
    policy = args.policy.lower()
    max_inst = getattr(args, "max_instances", 1) or 1
    try:
        set_concurrency(args.expression, policy, max_inst)
        print(f"Concurrency policy '{policy}' (max {max_inst}) set for: {args.expression}")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_concurrency_get(args) -> None:
    entry = get_concurrency(args.expression)
    if entry is None:
        print(f"No concurrency policy found for: {args.expression}")
    else:
        desc = _describe(args.expression)
        print(f"Expression : {args.expression}")
        print(f"Description: {desc}")
        print(f"Policy     : {entry['policy']}")
        print(f"Max instances: {entry['max_instances']}")


def cmd_concurrency_delete(args) -> None:
    if delete_concurrency(args.expression):
        print(f"Concurrency policy removed for: {args.expression}")
    else:
        print(f"No concurrency policy found for: {args.expression}")


def cmd_concurrency_list(args) -> None:
    all_entries = list_concurrency()
    if not all_entries:
        print("No concurrency policies set.")
        return
    for expr, entry in all_entries.items():
        desc = _describe(expr)
        print(f"{expr}  [{entry['policy']}, max={entry['max_instances']}]  — {desc}")
