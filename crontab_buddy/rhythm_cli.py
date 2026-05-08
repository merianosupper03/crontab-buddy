"""CLI commands for rhythm assessment."""

import json

from crontab_buddy.rhythm import assess_rhythm, batch_rhythm


def cmd_rhythm_check(args) -> None:
    result = assess_rhythm(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Level      : {result.level}")
    print(f"Score      : {result.score:.4f}")
    print(f"Intervals  : {result.intervals}")


def cmd_rhythm_score(args) -> None:
    result = assess_rhythm(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(f"{result.score:.4f}")


def cmd_rhythm_level(args) -> None:
    result = assess_rhythm(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.level)


def cmd_rhythm_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_rhythm(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  error: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.level:12s}  {r.score:.4f}")


def cmd_rhythm_json(args) -> None:
    result = assess_rhythm(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "level": result.level,
        "intervals": result.intervals,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
