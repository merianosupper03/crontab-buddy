"""CLI commands for the intensity module."""

from __future__ import annotations
import json
from crontab_buddy.intensity import assess_intensity, batch_intensity


def cmd_intensity_check(args) -> None:
    result = assess_intensity(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    print(f"Runs/day   : {result.runs_per_day}")


def cmd_intensity_score(args) -> None:
    result = assess_intensity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_intensity_grade(args) -> None:
    result = assess_intensity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_intensity_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_intensity(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s} error: {r.error}")
        else:
            print(f"{r.expression!r:40s} {r.grade:12s} score={r.score:.4f}  runs/day={r.runs_per_day}")


def cmd_intensity_json(args) -> None:
    result = assess_intensity(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "runs_per_day": result.runs_per_day,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
