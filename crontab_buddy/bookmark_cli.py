"""CLI commands for bookmark management."""

from crontab_buddy.bookmark import add_bookmark, get_bookmark, delete_bookmark, list_bookmarks
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_bookmark_add(args) -> None:
    name = args.name
    expression = args.expression
    path = getattr(args, "path", None)
    kwargs = {"path": path} if path else {}
    ok = add_bookmark(name, expression, **kwargs)
    if ok:
        print(f"Bookmarked '{name}': {expression}")
        print(f"  {_describe(expression)}")
    else:
        print(f"Bookmark '{name}' already exists. Use delete first to overwrite.")


def cmd_bookmark_get(args) -> None:
    name = args.name
    path = getattr(args, "path", None)
    kwargs = {"path": path} if path else {}
    expr = get_bookmark(name, **kwargs)
    if expr is None:
        print(f"No bookmark found for '{name}'.")
    else:
        print(f"{name}: {expr}")
        print(f"  {_describe(expr)}")


def cmd_bookmark_delete(args) -> None:
    name = args.name
    path = getattr(args, "path", None)
    kwargs = {"path": path} if path else {}
    ok = delete_bookmark(name, **kwargs)
    if ok:
        print(f"Deleted bookmark '{name}'.")
    else:
        print(f"No bookmark named '{name}' found.")


def cmd_bookmark_list(args) -> None:
    path = getattr(args, "path", None)
    kwargs = {"path": path} if path else {}
    bookmarks = list_bookmarks(**kwargs)
    if not bookmarks:
        print("No bookmarks saved.")
        return
    for b in bookmarks:
        print(f"{b['name']}: {b['expression']}")
        print(f"  {_describe(b['expression'])}")
