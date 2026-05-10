"""CLI commands for latency assessment."""

from __future__ import annotations
import json
from crontab_buddy.latency import assess_latency, batch_latency


def cmd_latency_check(args) -> None:
    """Print a full latency report for a single expression."""
    result = assess_latency(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    minutes = (result.interval_seconds or 0) / 60
    print(f"Interval   : {minutes:.1f} minutes ({result.interval_seconds:.0f}s)")
    print(f"Grade      : {result.grade}")


def cmd_latency_grade(args) -> None:
    """Print only the latency grade."""
    result = assess_latency(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_latency_seconds(args) -> None:
    """Print the interval in seconds."""
    result = assess_latency(args.expression)
    if result.error:
        print(f"error: {result.error}")
    elif result.interval_seconds is not None:
        print(f"{result.interval_seconds:.0f}")


def cmd_latency_batch(args) -> None:
    """Assess latency for multiple expressions (one per line via stdin or list)."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_latency(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            minutes = (r.interval_seconds or 0) / 60
            print(f"{r.expression!r:40s}  {minutes:8.1f}m  {r.grade}")


def cmd_latency_json(args) -> None:
    """Output latency result as JSON."""
    result = assess_latency(args.expression)
    data = {
        "expression": result.expression,
        "interval_seconds": result.interval_seconds,
        "grade": result.grade,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
