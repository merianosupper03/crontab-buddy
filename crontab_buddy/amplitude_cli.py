"""CLI commands for amplitude analysis."""

from __future__ import annotations
import json
from crontab_buddy.amplitude import assess_amplitude, batch_amplitude


def cmd_amplitude_check(args) -> None:
    result = assess_amplitude(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    for name, s in result.scores.items():
        print(f"  {name:<8}: {s:.4f}")


def cmd_amplitude_score(args) -> None:
    result = assess_amplitude(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_amplitude_grade(args) -> None:
    result = assess_amplitude(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_amplitude_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_amplitude(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.score:.4f}  {r.grade}")


def cmd_amplitude_json(args) -> None:
    result = assess_amplitude(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
