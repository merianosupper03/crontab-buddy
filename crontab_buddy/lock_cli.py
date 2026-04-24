"""CLI commands for expression lock management."""

from __future__ import annotations

from crontab_buddy.lock import (
    lock_expression,
    unlock_expression,
    get_lock,
    is_locked,
    list_locks,
    clear_locks,
)


def _describe(info: dict) -> str:
    reason = info.get("reason") or "(no reason)"
    locked_at = info.get("locked_at", "unknown")
    return f"locked at {locked_at} — {reason}"


def cmd_lock_add(args) -> None:
    reason = getattr(args, "reason", "") or ""
    ok = lock_expression(args.expression, reason=reason, path=args.path)
    if ok:
        print(f"Locked: {args.expression}")
    else:
        print(f"Already locked: {args.expression}")


def cmd_lock_remove(args) -> None:
    ok = unlock_expression(args.expression, path=args.path)
    if ok:
        print(f"Unlocked: {args.expression}")
    else:
        print(f"Not locked: {args.expression}")


def cmd_lock_check(args) -> None:
    info = get_lock(args.expression, path=args.path)
    if info:
        print(f"{args.expression} is LOCKED — {_describe(info)}")
    else:
        print(f"{args.expression} is not locked")


def cmd_lock_list(args) -> None:
    locks = list_locks(path=args.path)
    if not locks:
        print("No locked expressions.")
        return
    for expr, info in locks.items():
        print(f"  {expr}  [{_describe(info)}]")


def cmd_lock_clear(args) -> None:
    n = clear_locks(path=args.path)
    print(f"Cleared {n} lock(s).")
