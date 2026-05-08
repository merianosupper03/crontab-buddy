"""CLI commands for turbulence assessment."""

from __future__ import annotations

import json

from crontab_buddy.turbulence import assess_turbulence, batch_turbulence


def cmd_turbulence_check(args) -> None:
    """Print a full turbulence report for a single expression."""
    result = assess_turbulence(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Label      : {result.label}")
    if result.intervals:
        print(f"Intervals  : {result.intervals}")


def cmd_turbulence_score(args) -> None:
    """Print only the turbulence score."""
    result = assess_turbulence(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.score)


def cmd_turbulence_label(args) -> None:
    """Print only the turbulence label."""
    result = assess_turbulence(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.label)


def cmd_turbulence_batch(args) -> None:
    """Print turbulence labels for multiple expressions."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_turbulence(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.label} ({r.score:.4f})")


def cmd_turbulence_json(args) -> None:
    """Emit turbulence result as JSON."""
    result = assess_turbulence(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "label": result.label,
        "intervals": result.intervals,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
