"""CLI commands for porosity assessment."""
from __future__ import annotations
import json
from crontab_buddy.porosity import assess_porosity, batch_porosity


def cmd_porosity_check(args) -> None:
    result = assess_porosity(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    for name, val in result.scores.items():
        print(f"  {name:<8}: {val:.4f}")


def cmd_porosity_score(args) -> None:
    result = assess_porosity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_porosity_grade(args) -> None:
    result = assess_porosity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_porosity_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_porosity(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.grade:<12}  {r.score:.4f}")


def cmd_porosity_json(args) -> None:
    result = assess_porosity(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
