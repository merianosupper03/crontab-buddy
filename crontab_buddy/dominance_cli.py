"""CLI commands for the dominance module."""

from __future__ import annotations
import json

from crontab_buddy.dominance import assess_dominance, batch_dominance


def cmd_dominance_check(args) -> None:
    result = assess_dominance(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    print(f"Fires/day  : {result.fires_per_day}")


def cmd_dominance_score(args) -> None:
    result = assess_dominance(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_dominance_grade(args) -> None:
    result = assess_dominance(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_dominance_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_dominance(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.grade:15s}  score={r.score:.4f}  fires/day={r.fires_per_day}")


def cmd_dominance_json(args) -> None:
    result = assess_dominance(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "fires_per_day": result.fires_per_day,
    }
    if result.error:
        data["error"] = result.error
    print(json.dumps(data, indent=2))
