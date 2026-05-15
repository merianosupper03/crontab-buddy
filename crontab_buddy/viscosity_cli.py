"""CLI commands for viscosity assessment."""

import json
from crontab_buddy.viscosity import assess_viscosity, batch_viscosity


def cmd_viscosity_check(args):
    result = assess_viscosity(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    for field, val in result.scores.items():
        print(f"  {field:<8}: {val:.4f}")


def cmd_viscosity_score(args):
    result = assess_viscosity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_viscosity_grade(args):
    result = assess_viscosity(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_viscosity_batch(args):
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_viscosity(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s} ERROR: {r.error}")
        else:
            print(f"{r.expression!r:40s} {r.score:.4f}  {r.grade}")


def cmd_viscosity_json(args):
    result = assess_viscosity(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
