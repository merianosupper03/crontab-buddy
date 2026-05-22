"""CLI commands for elasticity assessment."""

from __future__ import annotations
import json
from crontab_buddy.elasticity import assess_elasticity, batch_elasticity


def cmd_elasticity_check(args) -> None:
    result = assess_elasticity(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.3f}")
    for field, val in result.scores.items():
        print(f"  {field:<8}: {val:.3f}")


def cmd_elasticity_score(args) -> None:
    result = assess_elasticity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_elasticity_grade(args) -> None:
    result = assess_elasticity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_elasticity_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_elasticity(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s} ERROR: {r.error}")
        else:
            print(f"{r.expression!r:40s} {r.grade} ({r.score:.3f})")


def cmd_elasticity_json(args) -> None:
    result = assess_elasticity(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
