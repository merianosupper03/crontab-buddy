"""CLI commands for the uniformity module."""

import json
from crontab_buddy.uniformity import assess_uniformity, batch_uniformity


def cmd_uniformity_check(args) -> None:
    result = assess_uniformity(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    print(f"Firings/day: {len(result.intervals) + 1}")


def cmd_uniformity_score(args) -> None:
    result = assess_uniformity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_uniformity_grade(args) -> None:
    result = assess_uniformity(args.expression)
    print(result.grade)


def cmd_uniformity_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_uniformity(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  score={r.score:.4f}  grade={r.grade}")


def cmd_uniformity_json(args) -> None:
    result = assess_uniformity(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "firings_per_day": len(result.intervals) + 1 if not result.error else 0,
        "intervals_sample": result.intervals[:10],
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
