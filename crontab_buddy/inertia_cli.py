"""CLI commands for the inertia module."""

import json
from crontab_buddy.inertia import assess_inertia, batch_inertia


def cmd_inertia_check(args, print_fn=print):
    """Print a full inertia report for a single expression."""
    result = assess_inertia(args.expression)
    print_fn(f"Expression : {result.expression}")
    if result.error:
        print_fn(f"Error      : {result.error}")
        return
    print_fn(f"Score      : {result.score:.4f}")
    print_fn(f"Grade      : {result.grade}")
    print_fn(f"Interval   : {result.interval_seconds}s")
    print_fn(f"Description: {result.description}")


def cmd_inertia_score(args, print_fn=print):
    """Print only the numeric inertia score."""
    result = assess_inertia(args.expression)
    if result.error:
        print_fn(f"Error: {result.error}")
        return
    print_fn(f"{result.score:.4f}")


def cmd_inertia_grade(args, print_fn=print):
    """Print only the inertia grade label."""
    result = assess_inertia(args.expression)
    if result.error:
        print_fn(f"Error: {result.error}")
        return
    print_fn(result.grade)


def cmd_inertia_batch(args, print_fn=print):
    """Print inertia scores for multiple space-separated expressions."""
    expressions = args.expressions
    results = batch_inertia(expressions)
    for r in results:
        if r.error:
            print_fn(f"{r.expression!r:30s} ERROR: {r.error}")
        else:
            print_fn(f"{r.expression!r:30s} score={r.score:.4f}  grade={r.grade}")


def cmd_inertia_json(args, print_fn=print):
    """Output inertia result as JSON."""
    result = assess_inertia(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "interval_seconds": result.interval_seconds,
        "description": result.description,
        "error": result.error,
    }
    print_fn(json.dumps(data, indent=2))
