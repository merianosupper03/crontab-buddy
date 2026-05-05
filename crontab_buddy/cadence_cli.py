"""CLI commands for cadence analysis."""

from crontab_buddy.cadence import cadence_summary, classify_cadence, format_cadence
import json


def cmd_cadence_check(args, print_fn=print):
    """Print the cadence level for a cron expression."""
    level = classify_cadence(args.expression)
    print_fn(f"Cadence: {level}")


def cmd_cadence_summary(args, print_fn=print):
    """Print a full cadence summary for a cron expression."""
    summary = cadence_summary(args.expression)
    print_fn(f"Expression : {summary['expression']}")
    print_fn(f"Cadence    : {summary['cadence']}")
    print_fn(f"Recurrence : {summary['recurrence']}")
    interval = summary["interval_seconds"]
    print_fn(f"Interval   : {interval}s" if interval is not None else "Interval   : unknown")


def cmd_cadence_format(args, print_fn=print):
    """Print a human-readable cadence description."""
    print_fn(format_cadence(args.expression))


def cmd_cadence_json(args, print_fn=print):
    """Print cadence summary as JSON."""
    summary = cadence_summary(args.expression)
    print_fn(json.dumps(summary, indent=2))
