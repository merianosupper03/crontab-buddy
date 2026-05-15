"""CLI commands for the fading module."""

from __future__ import annotations
import json
from crontab_buddy.fading import assess_fading, batch_fading


def cmd_fading_check(args) -> None:
    result = assess_fading(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Label      : {result.label}")
    print(f"Score      : {result.score:.3f}")
    print(f"Grade      : {result.grade}")
    if result.interval_seconds is not None:
        print(f"Interval   : {result.interval_seconds:.0f}s")


def cmd_fading_score(args) -> None:
    result = assess_fading(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"{result.score:.4f}")


def cmd_fading_grade(args) -> None:
    result = assess_fading(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.grade)


def cmd_fading_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_fading(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.label:10s}  score={r.score:.3f}  grade={r.grade}")


def cmd_fading_json(args) -> None:
    result = assess_fading(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "label": result.label,
        "grade": result.grade,
        "interval_seconds": result.interval_seconds,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
