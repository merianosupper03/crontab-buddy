"""CLI commands for scarcity analysis."""
from __future__ import annotations
import json
from crontab_buddy.scarcity import assess_scarcity, batch_scarcity


def cmd_scarcity_check(args) -> None:
    """Print a full scarcity report for an expression."""
    result = assess_scarcity(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.3f}")
    print(f"Fires/day  : {result.firing_minutes}")


def cmd_scarcity_score(args) -> None:
    """Print only the numeric scarcity score."""
    result = assess_scarcity(args.expression)
    if result.error:
        print(f"Error: {result.error}")
        return
    print(f"{result.score:.4f}")


def cmd_scarcity_grade(args) -> None:
    """Print only the scarcity grade label."""
    result = assess_scarcity(args.expression)
    if result.error:
        print(f"Error: {result.error}")
        return
    print(result.grade)


def cmd_scarcity_batch(args) -> None:
    """Print scarcity grades for multiple expressions."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_scarcity(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.grade:12s}  {r.score:.3f}")


def cmd_scarcity_json(args) -> None:
    """Emit scarcity result as JSON."""
    result = assess_scarcity(args.expression)
    data = {
        "expression": result.expression,
        "firing_minutes": result.firing_minutes,
        "score": result.score,
        "grade": result.grade,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
