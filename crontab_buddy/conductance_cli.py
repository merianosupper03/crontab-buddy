"""CLI commands for conductance analysis."""

from __future__ import annotations
import json

from crontab_buddy.conductance import assess_conductance, batch_conductance


def cmd_conductance_check(args) -> None:
    result = assess_conductance(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    print(f"Active min : {result.active_minutes} / 1440")


def cmd_conductance_score(args) -> None:
    result = assess_conductance(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_conductance_grade(args) -> None:
    result = assess_conductance(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_conductance_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_conductance(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.grade:20s}  score={r.score:.4f}")


def cmd_conductance_json(args) -> None:
    result = assess_conductance(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "active_minutes": result.active_minutes,
    }
    if result.error:
        data["error"] = result.error
    print(json.dumps(data, indent=2))
