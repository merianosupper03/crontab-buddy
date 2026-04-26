"""CLI commands for ownership management."""

from __future__ import annotations

from crontab_buddy.ownership import (
    delete_owner,
    find_by_owner,
    find_by_team,
    get_owner,
    list_owners,
    set_owner,
)


def _describe(record: dict) -> str:
    parts = [record["expression"], f"owner={record['owner']}"]
    if record.get("team"):
        parts.append(f"team={record['team']}")
    if record.get("email"):
        parts.append(f"email={record['email']}")
    return "  ".join(parts)


def cmd_ownership_set(args) -> None:
    set_owner(
        args.expression,
        args.owner,
        team=getattr(args, "team", None),
        email=getattr(args, "email", None),
        path=args.path,
    )
    print(f"Owner '{args.owner}' set for: {args.expression}")


def cmd_ownership_get(args) -> None:
    record = get_owner(args.expression, path=args.path)
    if record is None:
        print(f"No owner found for: {args.expression}")
    else:
        print(_describe({"expression": args.expression, **record}))


def cmd_ownership_delete(args) -> None:
    removed = delete_owner(args.expression, path=args.path)
    if removed:
        print(f"Ownership removed for: {args.expression}")
    else:
        print(f"No ownership record found for: {args.expression}")


def cmd_ownership_list(args) -> None:
    records = list_owners(path=args.path)
    if not records:
        print("No ownership records found.")
        return
    for r in records:
        print(_describe(r))


def cmd_ownership_find_owner(args) -> None:
    records = find_by_owner(args.owner, path=args.path)
    if not records:
        print(f"No expressions owned by '{args.owner}'.")
        return
    for r in records:
        print(_describe(r))


def cmd_ownership_find_team(args) -> None:
    records = find_by_team(args.team, path=args.path)
    if not records:
        print(f"No expressions found for team '{args.team}'.")
        return
    for r in records:
        print(_describe(r))
