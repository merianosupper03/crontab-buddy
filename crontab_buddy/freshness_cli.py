"""CLI commands for freshness assessment."""

import json
from datetime import datetime, timezone

from crontab_buddy.freshness import assess_freshness, batch_freshness
from crontab_buddy.history import get_history


def _parse_iso(s: str) -> datetime:
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError as exc:
        raise ValueError(f"Invalid ISO datetime: {s!r}") from exc


def cmd_freshness_check(args, print_fn=print):
    """Check freshness for a single expression with an optional last-seen date."""
    last_seen = None
    if hasattr(args, "last_seen") and args.last_seen:
        try:
            last_seen = _parse_iso(args.last_seen)
        except ValueError as exc:
            print_fn(f"Error: {exc}")
            return

    result = assess_freshness(args.expression, last_seen)
    print_fn(str(result))


def cmd_freshness_history(args, print_fn=print):
    """Assess freshness of all entries in history using their timestamps."""
    history = get_history()
    if not history:
        print_fn("No history entries found.")
        return

    entries = []
    for entry in history:
        expr = entry.get("expression", "")
        ts_str = entry.get("timestamp")
        ts = None
        if ts_str:
            try:
                ts = _parse_iso(ts_str)
            except ValueError:
                pass
        entries.append((expr, ts))

    results = batch_freshness(entries)
    for r in results:
        print_fn(str(r))


def cmd_freshness_json(args, print_fn=print):
    """Output freshness result as JSON."""
    last_seen = None
    if hasattr(args, "last_seen") and args.last_seen:
        try:
            last_seen = _parse_iso(args.last_seen)
        except ValueError as exc:
            print_fn(json.dumps({"error": str(exc)}))
            return

    result = assess_freshness(args.expression, last_seen)
    data = {
        "expression": result.expression,
        "last_seen": result.last_seen.isoformat() if result.last_seen else None,
        "days_since": result.days_since,
        "label": result.label,
        "score": result.score,
    }
    print_fn(json.dumps(data, indent=2))
