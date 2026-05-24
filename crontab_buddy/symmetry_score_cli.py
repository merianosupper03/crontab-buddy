"""CLI commands for symmetry score."""
from __future__ import annotations
import json
from crontab_buddy.symmetry_score import compute_symmetry_score


def cmd_symmetry_score_check(args) -> None:
    result = compute_symmetry_score(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    print(f"Firing mins: {result.firing_count}")


def cmd_symmetry_score_grade(args) -> None:
    result = compute_symmetry_score(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_symmetry_score_value(args) -> None:
    result = compute_symmetry_score(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(f"{result.score:.4f}")


def cmd_symmetry_score_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    for expr in expressions:
        result = compute_symmetry_score(expr)
        if result.error:
            print(f"{expr!r:40s}  error: {result.error}")
        else:
            print(f"{expr!r:40s}  score={result.score:.4f}  grade={result.grade}")


def cmd_symmetry_score_json(args) -> None:
    result = compute_symmetry_score(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "firing_count": result.firing_count,
    }
    if result.error:
        data["error"] = result.error
    print(json.dumps(data, indent=2))
