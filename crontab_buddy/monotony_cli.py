"""CLI commands for monotony analysis."""

from __future__ import annotations
import json

from crontab_buddy.monotony import assess_monotony, batch_monotony


def cmd_monotony_check(args) -> None:
    """Print a full monotony report for an expression."""
    result = assess_monotony(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    print("Field scores:")
    for name, score in result.scores.items():
        print(f"  {name:<8} {score:.4f}")


def cmd_monotony_score(args) -> None:
    """Print only the monotony score."""
    result = assess_monotony(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"{result.score:.4f}")


def cmd_monotony_grade(args) -> None:
    """Print only the monotony grade label."""
    result = assess_monotony(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.grade)


def cmd_monotony_batch(args) -> None:
    """Print monotony grades for multiple expressions."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_monotony(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.score:.4f}  {r.grade}")


def cmd_monotony_json(args) -> None:
    """Output monotony result as JSON."""
    result = assess_monotony(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
