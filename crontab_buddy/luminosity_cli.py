"""CLI commands for luminosity assessment."""

from __future__ import annotations
import json
from crontab_buddy.luminosity import assess_luminosity, batch_luminosity


def cmd_luminosity_check(args) -> None:
    """Print full luminosity report for an expression."""
    result = assess_luminosity(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    print(f"Peak ratio : {result.peak_ratio:.4f}")


def cmd_luminosity_score(args) -> None:
    """Print only the numeric luminosity score."""
    result = assess_luminosity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(f"{result.score:.4f}")


def cmd_luminosity_grade(args) -> None:
    """Print only the luminosity grade label."""
    result = assess_luminosity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_luminosity_batch(args) -> None:
    """Print luminosity grades for multiple space-separated expressions."""
    expressions = args.expressions
    results = batch_luminosity(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.grade:10s}  {r.score:.4f}")


def cmd_luminosity_json(args) -> None:
    """Emit luminosity result as JSON."""
    result = assess_luminosity(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "peak_ratio": result.peak_ratio,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
