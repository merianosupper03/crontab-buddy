"""CLI commands for curvature analysis."""

import json
from crontab_buddy.curvature import assess_curvature, batch_curvature


def cmd_curvature_check(args) -> None:
    result = assess_curvature(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")


def cmd_curvature_score(args) -> None:
    result = assess_curvature(args.expression)
    if result.error:
        print(f"Error: {result.error}")
        return
    print(result.score)


def cmd_curvature_grade(args) -> None:
    result = assess_curvature(args.expression)
    if result.error:
        print(f"Error: {result.error}")
        return
    print(result.grade)


def cmd_curvature_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_curvature(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:30s}  score={r.score:.4f}  grade={r.grade}")


def cmd_curvature_json(args) -> None:
    result = assess_curvature(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
