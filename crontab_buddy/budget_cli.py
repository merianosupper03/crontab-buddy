"""CLI commands for the budget feature."""

from __future__ import annotations

from typing import Any

from crontab_buddy.budget import (
    VALID_PERIODS,
    delete_budget,
    get_budget,
    list_budgets,
    set_budget,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_budget_set(args: Any) -> None:
    try:
        max_runs = int(args.max_runs)
    except (TypeError, ValueError):
        print("Error: max_runs must be an integer")
        return
    if args.period not in VALID_PERIODS:
        print(f"Error: period must be one of {VALID_PERIODS}")
        return
    try:
        set_budget(args.expression, max_runs, args.period, path=args.path)
        print(f"Budget set: {args.expression} — {max_runs} runs per {args.period}")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_budget_get(args: Any) -> None:
    entry = get_budget(args.expression, path=args.path)
    if entry is None:
        print(f"No budget found for: {args.expression}")
        return
    desc = _describe(args.expression)
    print(f"{args.expression}  [{desc}]")
    print(f"  max_runs : {entry['max_runs']}")
    print(f"  period   : {entry['period']}")


def cmd_budget_delete(args: Any) -> None:
    removed = delete_budget(args.expression, path=args.path)
    if removed:
        print(f"Budget removed for: {args.expression}")
    else:
        print(f"No budget found for: {args.expression}")


def cmd_budget_list(args: Any) -> None:
    entries = list_budgets(path=args.path)
    if not entries:
        print("No budgets saved.")
        return
    for entry in entries:
        desc = _describe(entry["expression"])
        print(
            f"{entry['expression']}  [{desc}]  "
            f"max={entry['max_runs']} / {entry['period']}"
        )
