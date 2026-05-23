"""CLI commands for the clutter module."""

import json
from crontab_buddy.clutter import assess_clutter, batch_clutter


def cmd_clutter_check(args):
    result = assess_clutter(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    for name, s in result.scores.items():
        print(f"  {name:<8}: {s:.4f}")


def cmd_clutter_score(args):
    result = assess_clutter(args.expression)
    if result.error:
        print(f"error: {result.error}")
        return
    print(result.score)


def cmd_clutter_grade(args):
    result = assess_clutter(args.expression)
    print(result.grade)


def cmd_clutter_batch(args):
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_clutter(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.grade:<12}  {r.score:.4f}")


def cmd_clutter_json(args):
    result = assess_clutter(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
    }
    if result.error:
        data["error"] = result.error
    print(json.dumps(data, indent=2))
