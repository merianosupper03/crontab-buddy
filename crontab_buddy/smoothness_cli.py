"""CLI commands for smoothness assessment."""

from __future__ import annotations
import json

from crontab_buddy.smoothness import assess_smoothness, batch_smoothness


def cmd_smoothness_check(args) -> None:
    result = assess_smoothness(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    print(f"Minutes    : {len(result.firing_minutes)} firing per hour")


def cmd_smoothness_score(args) -> None:
    result = assess_smoothness(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_smoothness_grade(args) -> None:
    result = assess_smoothness(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_smoothness_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions.split(",") if e.strip()]
    results = batch_smoothness(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.grade:10s}  {r.score:.4f}")


def cmd_smoothness_json(args) -> None:
    result = assess_smoothness(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "firing_minutes_count": len(result.firing_minutes),
        "intervals": result.intervals,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
