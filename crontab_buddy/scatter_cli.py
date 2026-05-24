"""CLI commands for the scatter module."""
from __future__ import annotations
import json

from crontab_buddy.scatter import assess_scatter, batch_scatter


def cmd_scatter_check(args) -> None:
    result = assess_scatter(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    print(f"Spread     : {result.spread:.1f} min")
    print(f"Minutes    : {len(result.firing_minutes)} firing point(s)")


def cmd_scatter_score(args) -> None:
    result = assess_scatter(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_scatter_grade(args) -> None:
    result = assess_scatter(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_scatter_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions.split(",") if e.strip()]
    results = batch_scatter(expressions)
    for r in results:
        status = r.grade if not r.error else f"error: {r.error}"
        print(f"{r.expression:30s}  {status}")


def cmd_scatter_json(args) -> None:
    result = assess_scatter(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "spread": result.spread,
        "firing_minutes_count": len(result.firing_minutes),
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
