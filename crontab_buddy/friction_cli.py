"""CLI commands for friction analysis."""
from __future__ import annotations
import json
from crontab_buddy.friction import assess_friction, batch_friction


def cmd_friction_check(args) -> None:
    result = assess_friction(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    print("Field scores:")
    for name, val in result.scores.items():
        print(f"  {name:<8} {val:.4f}")


def cmd_friction_score(args) -> None:
    result = assess_friction(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_friction_grade(args) -> None:
    result = assess_friction(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_friction_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_friction(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  score={r.score:.4f}  grade={r.grade}")


def cmd_friction_json(args) -> None:
    result = assess_friction(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
