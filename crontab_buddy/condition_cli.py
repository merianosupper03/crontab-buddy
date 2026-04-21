"""CLI commands for managing conditional execution rules."""

from __future__ import annotations

from crontab_buddy.condition import (
    VALID_OPERATORS,
    add_condition,
    clear_conditions,
    get_conditions,
    list_all_conditions,
    remove_condition,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except CronParseError:
        return expr


def cmd_condition_add(args) -> None:
    if args.operator not in VALID_OPERATORS:
        print(f"Error: invalid operator '{args.operator}'. Valid: {', '.join(VALID_OPERATORS)}")
        return
    try:
        added = add_condition(args.expression, args.variable, args.operator, args.value)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    if added:
        print(f"Condition added: [{args.variable} {args.operator} {args.value}] for '{args.expression}'")
    else:
        print("Condition already exists.")


def cmd_condition_remove(args) -> None:
    removed = remove_condition(args.expression, args.variable, args.operator, args.value)
    if removed:
        print(f"Condition removed from '{args.expression}'.")
    else:
        print("Condition not found.")


def cmd_condition_list(args) -> None:
    conditions = get_conditions(args.expression)
    if not conditions:
        print(f"No conditions for '{args.expression}'.")
        return
    print(f"Conditions for '{args.expression}' ({_describe(args.expression)}):")
    for i, rule in enumerate(conditions, 1):
        print(f"  {i}. {rule['variable']} {rule['operator']} {rule['value']}")


def cmd_condition_clear(args) -> None:
    count = clear_conditions(args.expression)
    print(f"Cleared {count} condition(s) from '{args.expression}'.")


def cmd_condition_list_all(args) -> None:
    all_conditions = list_all_conditions()
    if not all_conditions:
        print("No conditions stored.")
        return
    for expr, rules in all_conditions.items():
        print(f"  {expr} — {_describe(expr)}")
        for rule in rules:
            print(f"    • {rule['variable']} {rule['operator']} {rule['value']}")
