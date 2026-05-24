"""CLI commands for directionality assessment."""
from __future__ import annotations
import json
from crontab_buddy.directionality import assess_directionality, batch_directionality


def cmd_directionality_check(args) -> None:
    result = assess_directionality(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Dominant   : {result.dominant_period}")
    print(f"Grade      : {result.grade}")
    for period, score in result.scores.items():
        bar = "#" * int(score * 20)
        print(f"  {period:<12} {score:.2f}  {bar}")


def cmd_directionality_period(args) -> None:
    result = assess_directionality(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.dominant_period)


def cmd_directionality_grade(args) -> None:
    result = assess_directionality(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_directionality_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_directionality(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.dominant_period:<12}  {r.grade}")


def cmd_directionality_json(args) -> None:
    result = assess_directionality(args.expression)
    payload = {
        "expression": result.expression,
        "dominant_period": result.dominant_period,
        "scores": result.scores,
        "grade": result.grade,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
