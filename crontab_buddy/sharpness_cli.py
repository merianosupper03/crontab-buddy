"""CLI commands for the sharpness module."""

import json
from crontab_buddy.sharpness import assess_sharpness, batch_sharpness


def cmd_sharpness_check(args):
    """Print a full sharpness report for an expression."""
    result = assess_sharpness(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    print("Field scores:")
    for name, val in result.scores.items():
        print(f"  {name:<8} {val:.4f}")


def cmd_sharpness_score(args):
    """Print only the numeric sharpness score."""
    result = assess_sharpness(args.expression)
    if result.error:
        print(f"Error: {result.error}")
        return
    print(result.score)


def cmd_sharpness_grade(args):
    """Print only the sharpness grade label."""
    result = assess_sharpness(args.expression)
    if result.error:
        print(f"Error: {result.error}")
        return
    print(result.grade)


def cmd_sharpness_batch(args):
    """Print sharpness grades for multiple expressions."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_sharpness(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.score:.4f}  {r.grade}")


def cmd_sharpness_json(args):
    """Output sharpness result as JSON."""
    result = assess_sharpness(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
