"""CLI commands for saturation analysis."""
from __future__ import annotations
import json
from crontab_buddy.saturation import assess_saturation


def cmd_saturation_check(args) -> None:
    result = assess_saturation(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    for field, score in result.scores.items():
        bar = int(score * 20)
        print(f"  {field:<8}: {'#' * bar:<20} {score:.2f}")
    print(f"Overall    : {result.overall:.2f}  ({result.grade})")


def cmd_saturation_grade(args) -> None:
    result = assess_saturation(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_saturation_score(args) -> None:
    result = assess_saturation(args.expression)
    if result.error:
        print("0.0")
    else:
        print(f"{result.overall:.4f}")


def cmd_saturation_batch(args) -> None:
    expressions = args.expressions
    for expr in expressions:
        result = assess_saturation(expr)
        if result.error:
            print(f"{expr!r:40s}  error: {result.error}")
        else:
            print(f"{expr!r:40s}  {result.overall:.2f}  {result.grade}")


def cmd_saturation_json(args) -> None:
    result = assess_saturation(args.expression)
    data = {
        "expression": result.expression,
        "scores": result.scores,
        "overall": result.overall,
        "grade": result.grade,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
