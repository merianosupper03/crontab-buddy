"""CLI commands for expression feedback."""
from __future__ import annotations

from typing import Any

from crontab_buddy.feedback import (
    VALID_SENTIMENTS,
    add_feedback,
    delete_feedback,
    feedback_summary,
    get_feedback,
    list_all_feedback,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_feedback_add(args: Any, path: str | None = None) -> None:
    kwargs = {"path": path} if path else {}
    if args.sentiment not in VALID_SENTIMENTS:
        print(f"Error: sentiment must be one of {VALID_SENTIMENTS}")
        return
    add_feedback(args.expression, args.sentiment, getattr(args, "comment", ""), **kwargs)
    print(f"Feedback recorded for '{args.expression}': {args.sentiment}")


def cmd_feedback_get(args: Any, path: str | None = None) -> None:
    kwargs = {"path": path} if path else {}
    entries = get_feedback(args.expression, **kwargs)
    if not entries:
        print(f"No feedback for '{args.expression}'.")
        return
    print(f"Feedback for '{args.expression}' ({_describe(args.expression)}):")
    for e in entries:
        ts = e.get("timestamp", "")[:19].replace("T", " ")
        comment = f" — {e['comment']}" if e.get("comment") else ""
        print(f"  [{ts}] {e['sentiment']}{comment}")


def cmd_feedback_delete(args: Any, path: str | None = None) -> None:
    kwargs = {"path": path} if path else {}
    if delete_feedback(args.expression, **kwargs):
        print(f"Feedback deleted for '{args.expression}'.")
    else:
        print(f"No feedback found for '{args.expression}'.")


def cmd_feedback_summary(args: Any, path: str | None = None) -> None:
    kwargs = {"path": path} if path else {}
    summary = feedback_summary(args.expression, **kwargs)
    print(f"Summary for '{args.expression}':")
    for key, val in summary.items():
        print(f"  {key}: {val}")


def cmd_feedback_list(args: Any, path: str | None = None) -> None:
    kwargs = {"path": path} if path else {}
    all_fb = list_all_feedback(**kwargs)
    if not all_fb:
        print("No feedback stored.")
        return
    for expr, entries in all_fb.items():
        print(f"{expr} ({_describe(expr)}): {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}")
