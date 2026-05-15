"""CLI commands for the resolution module."""

from __future__ import annotations
import json
from crontab_buddy.resolution import assess_resolution, batch_resolution


def cmd_resolution_check(args) -> None:
    result = assess_resolution(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    for field, s in result.scores.items():
        print(f"  {field:<8}: {s:.4f}")


def cmd_resolution_score(args) -> None:
    result = assess_resolution(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_resolution_grade(args) -> None:
    result = assess_resolution(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_resolution_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_resolution(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  score={r.score:.4f}  grade={r.grade}")


def cmd_resolution_json(args) -> None:
    result = assess_resolution(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
