"""CLI commands for heartbeat tracking."""
from __future__ import annotations

import time

from crontab_buddy.heartbeat import (
    clear_heartbeats,
    get_heartbeats,
    latest_heartbeat,
    list_heartbeats,
    record_heartbeat,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_heartbeat_ping(args) -> None:
    """Record a heartbeat ping for an expression."""
    status = getattr(args, "status", "ok") or "ok"
    try:
        record_heartbeat(args.expression, status=status)
        print(f"Heartbeat recorded: {args.expression} [{status}]")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_heartbeat_get(args) -> None:
    """Show recent heartbeats for an expression."""
    records = get_heartbeats(args.expression)
    if not records:
        print(f"No heartbeats found for: {args.expression}")
        return
    print(f"Heartbeats for {args.expression} ({_describe(args.expression)}):")
    for rec in records[:10]:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(rec["timestamp"]))
        print(f"  [{rec['status'].upper()}] {ts}")


def cmd_heartbeat_latest(args) -> None:
    """Show the most recent heartbeat for an expression."""
    rec = latest_heartbeat(args.expression)
    if rec is None:
        print(f"No heartbeats found for: {args.expression}")
        return
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(rec["timestamp"]))
    print(f"Latest heartbeat: [{rec['status'].upper()}] {ts}")


def cmd_heartbeat_clear(args) -> None:
    """Clear all heartbeats for an expression."""
    removed = clear_heartbeats(args.expression)
    if removed:
        print(f"Cleared heartbeats for: {args.expression}")
    else:
        print(f"No heartbeats found for: {args.expression}")


def cmd_heartbeat_list(args) -> None:
    """List all expressions with heartbeat records."""
    data = list_heartbeats()
    if not data:
        print("No heartbeat records found.")
        return
    for expr, records in data.items():
        latest = max(records, key=lambda r: r["timestamp"])
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(latest["timestamp"]))
        print(f"  {expr} — last: [{latest['status'].upper()}] {ts} ({len(records)} total)")
