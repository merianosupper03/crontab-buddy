"""CLI commands for friction_score."""

from __future__ import annotations
import json

from crontab_buddy.friction_score import compute_friction_score


def cmd_friction_score_check(args) -> None:
    result = compute_friction_score(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    for field, val in result.scores.items():
        print(f"  {field:<8}: {val:.4f}")


def cmd_friction_score_grade(args) -> None:
    result = compute_friction_score(args.expression)
    print(result.grade if not result.error else f"error: {result.error}")


def cmd_friction_score_value(args) -> None:
    result = compute_friction_score(args.expression)
    print(f"{result.score:.4f}" if not result.error else f"error: {result.error}")


def cmd_friction_score_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions.split(",") if e.strip()]
    for expr in expressions:
        result = compute_friction_score(expr)
        if result.error:
            print(f"{expr} -> error: {result.error}")
        else:
            print(f"{expr} -> {result.score:.4f} ({result.grade})")


def cmd_friction_score_json(args) -> None:
    result = compute_friction_score(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
    }
    if result.error:
        data["error"] = result.error
    print(json.dumps(data, indent=2))
