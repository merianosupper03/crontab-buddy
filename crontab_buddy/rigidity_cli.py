"""CLI commands for rigidity assessment."""

import json
from crontab_buddy.rigidity import assess_rigidity, batch_rigidity


def cmd_rigidity_check(args, print_fn=print):
    result = assess_rigidity(args.expression)
    print_fn(f"Expression : {result.expression}")
    if result.error:
        print_fn(f"Error      : {result.error}")
        return
    print_fn(f"Grade      : {result.grade}")
    print_fn(f"Score      : {result.score}")
    for field, val in result.scores.items():
        print_fn(f"  {field:<8}: {val}")


def cmd_rigidity_score(args, print_fn=print):
    result = assess_rigidity(args.expression)
    if result.error:
        print_fn(f"Error: {result.error}")
        return
    print_fn(str(result.score))


def cmd_rigidity_grade(args, print_fn=print):
    result = assess_rigidity(args.expression)
    if result.error:
        print_fn(f"Error: {result.error}")
        return
    print_fn(result.grade)


def cmd_rigidity_batch(args, print_fn=print):
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_rigidity(expressions)
    for r in results:
        if r.error:
            print_fn(f"{r.expression!r:30s}  ERROR: {r.error}")
        else:
            print_fn(f"{r.expression!r:30s}  {r.grade:<12}  {r.score}")


def cmd_rigidity_json(args, print_fn=print):
    result = assess_rigidity(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print_fn(json.dumps(data, indent=2))
