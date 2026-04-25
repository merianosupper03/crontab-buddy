"""CLI commands for checkpoint management."""

from __future__ import annotations

from crontab_buddy.checkpoint import (
    save_checkpoint,
    get_checkpoint,
    delete_checkpoint,
    list_checkpoints,
    search_checkpoints,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_checkpoint_save(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    note = getattr(args, "note", "") or ""
    save_checkpoint(args.name, args.expression, note=note, **kwargs)
    print(f"Checkpoint '{args.name}' saved for: {args.expression}")


def cmd_checkpoint_get(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    cp = get_checkpoint(args.name, **kwargs)
    if cp is None:
        print(f"No checkpoint named '{args.name}'.")
        return
    print(f"Name      : {args.name}")
    print(f"Expression: {cp['expression']}")
    print(f"Description: {_describe(cp['expression'])}")
    if cp.get("note"):
        print(f"Note      : {cp['note']}")
    print(f"Saved at  : {cp['saved_at']}")


def cmd_checkpoint_delete(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    removed = delete_checkpoint(args.name, **kwargs)
    if removed:
        print(f"Checkpoint '{args.name}' deleted.")
    else:
        print(f"No checkpoint named '{args.name}'.")


def cmd_checkpoint_list(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    checkpoints = list_checkpoints(**kwargs)
    if not checkpoints:
        print("No checkpoints saved.")
        return
    for cp in checkpoints:
        desc = _describe(cp["expression"])
        note_str = f"  [{cp['note']}]" if cp.get("note") else ""
        print(f"{cp['name']}: {cp['expression']} — {desc}{note_str}")


def cmd_checkpoint_search(args, path=None) -> None:
    kwargs = {"path": path} if path else {}
    results = search_checkpoints(args.query, **kwargs)
    if not results:
        print(f"No checkpoints matching '{args.query}'.")
        return
    for cp in results:
        desc = _describe(cp["expression"])
        print(f"{cp['name']}: {cp['expression']} — {desc}")
