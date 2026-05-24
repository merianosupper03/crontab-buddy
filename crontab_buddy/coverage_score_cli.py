"""coverage_score_cli.py — CLI commands for coverage score."""

from __future__ import annotations

import json
from typing import List

from crontab_buddy.coverage_score import compute_coverage_score, batch_coverage_score


def cmd_coverage_score_check(args) -> None:
    """Print a human-readable coverage score for one expression."""
    result = compute_coverage_score(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.2f}")
    print(f"Grade      : {result.grade}")
    print(f"Hours      : {len(result.covered_hours)} / {result.total_hours}")


def cmd_coverage_score_grade(args) -> None:
    result = compute_coverage_score(args.expression)
    print(result.grade if not result.error else f"error: {result.error}")


def cmd_coverage_score_value(args) -> None:
    result = compute_coverage_score(args.expression)
    print(f"{result.score:.4f}" if not result.error else f"error: {result.error}")


def cmd_coverage_score_batch(args) -> None:
    """Score a whitespace-separated list of expressions."""
    expressions: List[str] = args.expressions
    results = batch_coverage_score(expressions)
    for r in results:
        status = f"{r.score:.2f} [{r.grade}]" if not r.error else f"ERROR: {r.error}"
        print(f"{r.expression:<30} {status}")


def cmd_coverage_score_json(args) -> None:
    result = compute_coverage_score(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "covered_hours": result.covered_hours,
        "total_hours": result.total_hours,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
