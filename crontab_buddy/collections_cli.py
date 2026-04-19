"""CLI commands for managing cron expression collections."""
from crontab_buddy.collections import (
    add_to_collection, remove_from_collection,
    get_collection, list_collections, delete_collection
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except CronParseError:
        return "(invalid)"


def cmd_collection_add(args, path=None):
    kwargs = {"path": path} if path else {}
    ok = add_to_collection(args.name, args.expression, **kwargs)
    if ok:
        print(f"Added '{args.expression}' to collection '{args.name}'.")
    else:
        print(f"'{args.expression}' is already in collection '{args.name}'.")


def cmd_collection_remove(args, path=None):
    kwargs = {"path": path} if path else {}
    ok = remove_from_collection(args.name, args.expression, **kwargs)
    if ok:
        print(f"Removed '{args.expression}' from collection '{args.name}'.")
    else:
        print(f"'{args.expression}' not found in collection '{args.name}'.")


def cmd_collection_list(args, path=None):
    kwargs = {"path": path} if path else {}
    col = get_collection(args.name, **kwargs)
    if col is None:
        print(f"Collection '{args.name}' does not exist.")
        return
    if not col:
        print(f"Collection '{args.name}' is empty.")
        return
    for expr in col:
        print(f"  {expr}  —  {_describe(expr)}")


def cmd_collection_delete(args, path=None):
    kwargs = {"path": path} if path else {}
    ok = delete_collection(args.name, **kwargs)
    if ok:
        print(f"Deleted collection '{args.name}'.")
    else:
        print(f"Collection '{args.name}' not found.")


def cmd_collection_all(args, path=None):
    kwargs = {"path": path} if path else {}
    names = list_collections(**kwargs)
    if not names:
        print("No collections found.")
        return
    for name in names:
        col = get_collection(name, **kwargs)
        print(f"[{name}] ({len(col)} expression(s))")
