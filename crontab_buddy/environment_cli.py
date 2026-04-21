"""CLI commands for managing environment variables tied to cron expressions."""

from __future__ import annotations

from crontab_buddy.environment import (
    set_env_var,
    get_env_var,
    get_all_env_vars,
    delete_env_var,
    clear_env_vars,
    list_all_env_vars,
)


def cmd_env_set(args) -> None:
    """Set an environment variable for a cron expression."""
    set_env_var(args.expression, args.key, args.value)
    print(f"Set {args.key.upper()}={args.value} for '{args.expression}'")


def cmd_env_get(args) -> None:
    """Get a specific environment variable for a cron expression."""
    val = get_env_var(args.expression, args.key)
    if val is None:
        print(f"No variable '{args.key.upper()}' found for '{args.expression}'")
    else:
        print(f"{args.key.upper()}={val}")


def cmd_env_delete(args) -> None:
    """Delete an environment variable for a cron expression."""
    removed = delete_env_var(args.expression, args.key)
    if removed:
        print(f"Deleted '{args.key.upper()}' from '{args.expression}'")
    else:
        print(f"Variable '{args.key.upper()}' not found for '{args.expression}'")


def cmd_env_list(args) -> None:
    """List all environment variables for a cron expression."""
    env = get_all_env_vars(args.expression)
    if not env:
        print(f"No environment variables set for '{args.expression}'")
        return
    print(f"Environment variables for '{args.expression}':")
    for key, val in sorted(env.items()):
        print(f"  {key}={val}")


def cmd_env_clear(args) -> None:
    """Clear all environment variables for a cron expression."""
    clear_env_vars(args.expression)
    print(f"Cleared all environment variables for '{args.expression}'")


def cmd_env_list_all(args) -> None:
    """List environment variables for all stored expressions."""
    all_envs = list_all_env_vars()
    if not all_envs:
        print("No environment variables stored.")
        return
    for expr, env in sorted(all_envs.items()):
        print(f"\n{expr}:")
        for key, val in sorted(env.items()):
            print(f"  {key}={val}")
