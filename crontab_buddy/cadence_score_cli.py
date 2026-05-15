"""CLI commands for cadence scoring."""

from __future__ import annotations

import json
from typing import List

from crontab_buddy.cadence_score import compute_cadence_score


def cmd_cadence_score_check(args) -> None:
    """Print a human-readable cadence score report."""
    result = compute_cadence_score(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    print(f"Interval   : {result.interval_seconds}s")
    print(f"Complexity : {result.complexity_level}")
    print(f"Entropy    : {result.entropy_level}")
    print(f"Regularity : {result.regularity_grade}")


def cmd_cadence_score_grade(args) -> None:
    """Print only the letter grade."""
    result = compute_cadence_score(args.expression)
    print(result.grade)


def cmd_cadence_score_value(args) -> None:
    """Print only the numeric score."""
    result = compute_cadence_score(args.expression)
    print(f"{result.score:.4f}")


def cmd_cadence_score_batch(args) -> None:
    """Score multiple expressions, one per line."""
    expressions: List[str] = [e.strip() for e in args.expressions if e.strip()]
    for expr in expressions:
        result = compute_cadence_score(expr)
        if result.error:
            print(f"{expr!r:40s}  ERROR: {result.error}")
        else:
            print(f"{expr!r:40s}  score={result.score:.4f}  grade={result.grade}")


def cmd_cadence_score_json(args) -> None:
    """Emit the result as JSON."""
    result = compute_cadence_score(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "interval_seconds": result.interval_seconds,
        "complexity_level": result.complexity_level,
        "entropy_level": result.entropy_level,
        "regularity_grade": result.regularity_grade,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
