"""CLI commands for permission management."""
from __future__ import annotations

from crontab_buddy.permission import (
    delete_permission,
    get_all_permissions,
    get_permission,
    list_users_with_role,
    set_permission,
)


def _describe(expression: str, user: str, role: str) -> str:
    return f"{expression!r}  user={user}  role={role}"


def cmd_permission_set(args) -> None:
    try:
        set_permission(args.expression, args.user, args.role)
        print(f"Permission set: {_describe(args.expression, args.user, args.role)}")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_permission_get(args) -> None:
    role = get_permission(args.expression, args.user)
    if role is None:
        print(f"No permission found for user '{args.user}' on expression '{args.expression}'.")
    else:
        print(_describe(args.expression, args.user, role))


def cmd_permission_delete(args) -> None:
    removed = delete_permission(args.expression, args.user)
    if removed:
        print(f"Permission removed for user '{args.user}' on '{args.expression}'.")
    else:
        print(f"No permission found for user '{args.user}' on '{args.expression}'.")


def cmd_permission_list(args) -> None:
    perms = get_all_permissions(args.expression)
    if not perms:
        print(f"No permissions set for '{args.expression}'.")
        return
    for user, role in sorted(perms.items()):
        print(_describe(args.expression, user, role))


def cmd_permission_by_role(args) -> None:
    try:
        entries = list_users_with_role(args.role)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    if not entries:
        print(f"No users found with role '{args.role}'.")
        return
    for entry in entries:
        print(f"{entry['expression']!r}  user={entry['user']}  role={args.role}")
