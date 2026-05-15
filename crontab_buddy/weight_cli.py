"""CLI commands for the weight module."""

from __future__ import annotations
import json
from crontab_buddy.weight import assess_weight, batch_weight


def cmd_weight_check(args) -> None:
    """Print a full weight report for a cron expression."""
    result = assess_weight(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    print(f"Runs/day   : {result.runs_per_day:.1f}")


def cmd_weight_score(args) -> None:
    """Print only the numeric weight score."""
    result = assess_weight(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.score)


def cmd_weight_grade(args) -> None:
    """Print only the weight grade label."""
    result = assess_weight(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.grade)


def cmd_weight_batch(args) -> None:
    """Print weight grades for multiple space-separated expressions."""
    expressions = args.expressions
    results = batch_weight(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  error: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.grade:12s}  score={r.score:.4f}")


def cmd_weight_json(args) -> None:
    """Output weight result as JSON."""
    result = assess_weight(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "runs_per_day": result.runs_per_day,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
