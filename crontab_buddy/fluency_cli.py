"""CLI commands for fluency assessment."""
import json
from crontab_buddy.fluency import assess_fluency, batch_fluency


def cmd_fluency_check(args) -> None:
    result = assess_fluency(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.2f}")
    if result.notes:
        for note in result.notes:
            print(f"Note       : {note}")


def cmd_fluency_score(args) -> None:
    result = assess_fluency(args.expression)
    print(result.score)


def cmd_fluency_grade(args) -> None:
    result = assess_fluency(args.expression)
    print(result.grade)


def cmd_fluency_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_fluency(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.grade:10s}  {r.score:.2f}")


def cmd_fluency_json(args) -> None:
    result = assess_fluency(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "notes": result.notes,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
