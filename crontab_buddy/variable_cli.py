"""CLI commands for managing cron expression variables."""

from __future__ import annotations

from typing import Any

from crontab_buddy.variable import (
    delete_variable,
    expand_variable,
    get_variable,
    list_variables,
    set_variable,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_variable_set(args: Any) -> None:
    set_variable(args.name, args.expression, **_path_kwargs(args))
    print(f"Variable '{args.name.upper()}' set to: {args.expression}")
    print(f"  → {_describe(args.expression)}")


def cmd_variable_get(args: Any) -> None:
    expr = get_variable(args.name, **_path_kwargs(args))
    if expr is None:
        print(f"No variable named '{args.name.upper()}'.")
    else:
        print(f"{args.name.upper()} = {expr}")
        print(f"  → {_describe(expr)}")


def cmd_variable_delete(args: Any) -> None:
    removed = delete_variable(args.name, **_path_kwargs(args))
    if removed:
        print(f"Variable '{args.name.upper()}' deleted.")
    else:
        print(f"Variable '{args.name.upper()}' not found.")


def cmd_variable_list(args: Any) -> None:
    variables = list_variables(**_path_kwargs(args))
    if not variables:
        print("No variables saved.")
        return
    for v in variables:
        print(f"{v['name']} = {v['expression']}")
        print(f"  → {_describe(v['expression'])}")


def cmd_variable_expand(args: Any) -> None:
    expr = expand_variable(args.name, **_path_kwargs(args))
    if expr is None:
        print(f"Variable '{args.name.upper()}' not found.")
    else:
        print(expr)


def _path_kwargs(args: Any) -> dict:
    if hasattr(args, "path") and args.path is not None:
        from pathlib import Path
        return {"path": Path(args.path)}
    return {}
