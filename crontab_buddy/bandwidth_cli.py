"""CLI commands for the bandwidth module."""

import json
from crontab_buddy.bandwidth import assess_bandwidth, batch_bandwidth


def cmd_bandwidth_check(args) -> None:
    """Print a full bandwidth report for a single expression."""
    result = assess_bandwidth(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Runs/hour  : {result.runs_per_hour}")
    print(f"Runs/day   : {result.runs_per_day}")
    print(f"Score      : {result.score}")
    print(f"Grade      : {result.grade}")


def cmd_bandwidth_grade(args) -> None:
    """Print only the bandwidth grade for an expression."""
    result = assess_bandwidth(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_bandwidth_score(args) -> None:
    """Print only the numeric bandwidth score (0.0–1.0)."""
    result = assess_bandwidth(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_bandwidth_batch(args) -> None:
    """Print bandwidth grades for multiple expressions (one per line)."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_bandwidth(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.grade} ({r.score:.3f})")


def cmd_bandwidth_json(args) -> None:
    """Emit bandwidth result(s) as JSON."""
    expressions = getattr(args, "expressions", None)
    if expressions:
        results = batch_bandwidth([e.strip() for e in expressions if e.strip()])
        data = [r.__dict__ for r in results]
    else:
        data = assess_bandwidth(args.expression).__dict__
    print(json.dumps(data, indent=2))
