"""CLI commands for the impulse module."""

from __future__ import annotations
import json
from crontab_buddy.impulse import assess_impulse, batch_impulse


def cmd_impulse_check(args) -> None:
    """Print full impulse report for an expression."""
    result = assess_impulse(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    print(f"Firing/day : {result.firing_count}")


def cmd_impulse_score(args) -> None:
    """Print only the numeric impulse score."""
    result = assess_impulse(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(f"{result.score:.4f}")


def cmd_impulse_grade(args) -> None:
    """Print only the impulse grade label."""
    result = assess_impulse(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_impulse_batch(args) -> None:
    """Print impulse grades for multiple expressions."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_impulse(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  error: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.grade:12s}  {r.score:.4f}")


def cmd_impulse_json(args) -> None:
    """Output impulse result as JSON."""
    result = assess_impulse(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "firing_count": result.firing_count,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
