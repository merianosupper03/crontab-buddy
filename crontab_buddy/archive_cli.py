"""CLI commands for the archive feature."""
from __future__ import annotations
from crontab_buddy.archive import archive_expression, get_archive, delete_from_archive, clear_archive, search_archive
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid)"


def cmd_archive_add(args) -> None:
    reason = getattr(args, "reason", "") or ""
    entry = archive_expression(args.expression, reason=reason, path=args.path)
    print(f"Archived: {entry['expression']} — {_describe(entry['expression'])}")
    if reason:
        print(f"  Reason: {reason}")


def cmd_archive_delete(args) -> None:
    if delete_from_archive(args.expression, path=args.path):
        print(f"Removed '{args.expression}' from archive.")
    else:
        print(f"Expression '{args.expression}' not found in archive.")


def cmd_archive_list(args) -> None:
    entries = get_archive(path=args.path)
    if not entries:
        print("Archive is empty.")
        return
    for e in entries:
        desc = _describe(e["expression"])
        reason = f" [{e['reason']}]" if e.get("reason") else ""
        print(f"{e['expression']} — {desc}{reason}  (archived {e['archived_at']})")


def cmd_archive_search(args) -> None:
    results = search_archive(args.keyword, path=args.path)
    if not results:
        print("No matching archived expressions.")
        return
    for e in results:
        desc = _describe(e["expression"])
        print(f"{e['expression']} — {desc}")


def cmd_archive_clear(args) -> None:
    clear_archive(path=args.path)
    print("Archive cleared.")
