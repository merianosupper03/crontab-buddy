"""CLI commands for pacing analysis."""

from __future__ import annotations
import json

from crontab_buddy.pacing import assess_pacing, batch_pacing


def cmd_pacing_check(args) -> None:
    """Print a full pacing report for an expression."""
    result = assess_pacing(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    print(f"Fires/day  : {result.fires_per_day}")
    print(f"Hourly var : {result.hourly_variance:.4f}")


def cmd_pacing_score(args) -> None:
    """Print only the numeric pacing score."""
    result = assess_pacing(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.score)


def cmd_pacing_grade(args) -> None:
    """Print only the pacing grade label."""
    result = assess_pacing(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.grade)


def cmd_pacing_batch(args) -> None:
    """Print pacing grades for multiple expressions (one per line)."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_pacing(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.grade:10s}  score={r.score:.4f}")


def cmd_pacing_json(args) -> None:
    """Emit pacing result as JSON."""
    result = assess_pacing(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "fires_per_day": result.fires_per_day,
        "hourly_variance": result.hourly_variance,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
