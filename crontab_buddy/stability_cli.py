"""CLI commands for the stability module."""

import json
from crontab_buddy.stability import assess_stability


def cmd_stability_check(args) -> None:
    """Print a human-readable stability report for an expression."""
    result = assess_stability(args.expression)
    print(f"Expression : {result.expression}")
    print(f"Level      : {result.level}")
    print(f"Score      : {result.score:.4f}")
    if result.interval_seconds is not None:
        print(f"Interval   : {result.interval_seconds}s")
    else:
        print("Interval   : unknown")
    if result.notes:
        print("Notes      :")
        for note in result.notes:
            print(f"  - {note}")
    else:
        print("Notes      : none")


def cmd_stability_score(args) -> None:
    """Print only the numeric stability score."""
    result = assess_stability(args.expression)
    print(f"{result.score:.4f}")


def cmd_stability_level(args) -> None:
    """Print only the stability level label."""
    result = assess_stability(args.expression)
    print(result.level)


def cmd_stability_batch(args) -> None:
    """Assess stability for multiple space-separated expressions."""
    for expr_str in args.expressions:
        result = assess_stability(expr_str)
        print(f"{expr_str}  ->  {result.level} ({result.score:.4f})")


def cmd_stability_json(args) -> None:
    """Output stability result as JSON."""
    result = assess_stability(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "level": result.level,
        "interval_seconds": result.interval_seconds,
        "notes": result.notes,
    }
    print(json.dumps(payload, indent=2))
