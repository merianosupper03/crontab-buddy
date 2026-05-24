"""CLI commands for persistence scoring."""
from __future__ import annotations
import json
from crontab_buddy.persistence import assess_persistence, batch_persistence


def cmd_persistence_check(args) -> None:
    result = assess_persistence(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    if result.interval_seconds is not None:
        print(f"Interval   : {result.interval_seconds}s")


def cmd_persistence_score(args) -> None:
    result = assess_persistence(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_persistence_grade(args) -> None:
    result = assess_persistence(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_persistence_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_persistence(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  error: {r.error}")
        else:
            print(f"{r.expression!r:30s}  score={r.score:.4f}  grade={r.grade}")


def cmd_persistence_json(args) -> None:
    result = assess_persistence(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "interval_seconds": result.interval_seconds,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
