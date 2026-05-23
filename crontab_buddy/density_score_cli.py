"""CLI commands for density score."""

from __future__ import annotations

import json
from typing import List

from crontab_buddy.density_score import compute_density_score


def cmd_density_score_check(args) -> None:
    result = compute_density_score(args.expression)
    print(str(result))


def cmd_density_score_grade(args) -> None:
    result = compute_density_score(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_density_score_value(args) -> None:
    result = compute_density_score(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(f"{result.score:.4f}")


def cmd_density_score_batch(args) -> None:
    expressions: List[str] = args.expressions
    for expr in expressions:
        result = compute_density_score(expr)
        print(str(result))


def cmd_density_score_json(args) -> None:
    result = compute_density_score(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "fires_per_day": result.fires_per_day,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
