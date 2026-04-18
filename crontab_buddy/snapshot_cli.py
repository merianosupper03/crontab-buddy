"""CLI commands for snapshot management."""

from crontab_buddy.snapshot import save_snapshot, get_snapshot, delete_snapshot, list_snapshots
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_snapshot_save(name: str, expression: str, comment: str = "", path=None) -> None:
    kwargs = {"path": path} if path else {}
    save_snapshot(name, expression, comment, **kwargs)
    print(f"Snapshot '{name}' saved: {expression}")
    print(f"  {_describe(expression)}")


def cmd_snapshot_get(name: str, path=None) -> None:
    kwargs = {"path": path} if path else {}
    snap = get_snapshot(name, **kwargs)
    if snap is None:
        print(f"No snapshot found with name '{name}'.")
        return
    print(f"Name:       {name}")
    print(f"Expression: {snap['expression']}")
    print(f"Saved at:   {snap['saved_at']}")
    if snap.get("comment"):
        print(f"Comment:    {snap['comment']}")
    print(f"Meaning:    {_describe(snap['expression'])}")


def cmd_snapshot_delete(name: str, path=None) -> None:
    kwargs = {"path": path} if path else {}
    removed = delete_snapshot(name, **kwargs)
    if removed:
        print(f"Snapshot '{name}' deleted.")
    else:
        print(f"No snapshot named '{name}' found.")


def cmd_snapshot_list(path=None) -> None:
    kwargs = {"path": path} if path else {}
    snaps = list_snapshots(**kwargs)
    if not snaps:
        print("No snapshots saved.")
        return
    for s in snaps:
        comment = f" — {s['comment']}" if s.get("comment") else ""
        print(f"  {s['name']}: {s['expression']}{comment} (saved {s['saved_at']})")
