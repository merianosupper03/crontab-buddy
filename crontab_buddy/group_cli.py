"""CLI commands for managing expression groups."""

from crontab_buddy.group import (
    create_group, add_to_group, remove_from_group,
    get_group, delete_group, list_groups,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except CronParseError:
        return "(invalid expression)"


def cmd_group_create(args) -> None:
    """Create a new empty group."""
    created = create_group(args.name, path=getattr(args, "path", None))
    if created:
        print(f"Group '{args.name}' created.")
    else:
        print(f"Group '{args.name}' already exists.")


def cmd_group_add(args) -> None:
    """Add an expression to a group."""
    added = add_to_group(args.name, args.expression, path=getattr(args, "path", None))
    if added:
        print(f"Added '{args.expression}' to group '{args.name}'.")
        print(f"  {_describe(args.expression)}")
    else:
        print(f"'{args.expression}' is already in group '{args.name}' (or group missing).")


def cmd_group_remove(args) -> None:
    """Remove an expression from a group."""
    removed = remove_from_group(args.name, args.expression, path=getattr(args, "path", None))
    if removed:
        print(f"Removed '{args.expression}' from group '{args.name}'.")
    else:
        print(f"'{args.expression}' not found in group '{args.name}'.")


def cmd_group_list(args) -> None:
    """List all groups or expressions in a specific group."""
    name = getattr(args, "name", None)
    if name:
        expressions = get_group(name, path=getattr(args, "path", None))
        if expressions is None:
            print(f"Group '{name}' not found.")
            return
        if not expressions:
            print(f"Group '{name}' is empty.")
            return
        print(f"Group '{name}':")
        for expr in expressions:
            print(f"  {expr}  — {_describe(expr)}")
    else:
        groups = list_groups(path=getattr(args, "path", None))
        if not groups:
            print("No groups found.")
            return
        for g in groups:
            expressions = get_group(g, path=getattr(args, "path", None)) or []
            print(f"  {g} ({len(expressions)} expression(s))")


def cmd_group_delete(args) -> None:
    """Delete an entire group."""
    deleted = delete_group(args.name, path=getattr(args, "path", None))
    if deleted:
        print(f"Group '{args.name}' deleted.")
    else:
        print(f"Group '{args.name}' not found.")
