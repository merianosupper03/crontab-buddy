"""CLI commands for fuzziness assessment."""

import json
from crontab_buddy.fuzziness import assess_fuzziness, batch_fuzziness


def cmd_fuzziness_check(args):
    result = assess_fuzziness(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Overall    : {result.overall:.3f}")
    print(f"Grade      : {result.grade}")
    for field, score in result.scores.items():
        print(f"  {field:<8}: {score:.3f}")


def cmd_fuzziness_score(args):
    result = assess_fuzziness(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.overall)


def cmd_fuzziness_grade(args):
    result = assess_fuzziness(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_fuzziness_batch(args):
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_fuzziness(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  error: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.overall:.3f}  {r.grade}")


def cmd_fuzziness_json(args):
    result = assess_fuzziness(args.expression)
    data = {
        "expression": result.expression,
        "overall": result.overall,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
