"""CLI commands for the evenness module."""
from __future__ import annotations
import json
from crontab_buddy.evenness import assess_evenness, batch_evenness


def cmd_evenness_check(args) -> None:
    result = assess_evenness(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
    else:
        print(f"Grade      : {result.grade}")
        print(f"Score      : {result.score:.4f}")


def cmd_evenness_score(args) -> None:
    result = assess_evenness(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_evenness_grade(args) -> None:
    result = assess_evenness(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_evenness_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_evenness(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.grade:20s}  {r.score:.4f}")


def cmd_evenness_json(args) -> None:
    result = assess_evenness(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
