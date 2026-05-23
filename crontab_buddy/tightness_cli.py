"""CLI commands for tightness analysis."""
import json
from crontab_buddy.tightness import assess_tightness, batch_tightness


def cmd_tightness_check(args) -> None:
    result = assess_tightness(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.3f}")
    print(f"Grade      : {result.grade}")
    print("Field scores:")
    for field, s in result.scores.items():
        print(f"  {field:<8}: {s:.3f}")


def cmd_tightness_score(args) -> None:
    result = assess_tightness(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(f"{result.score:.4f}")


def cmd_tightness_grade(args) -> None:
    result = assess_tightness(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_tightness_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_tightness(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.score:.3f}  {r.grade}")


def cmd_tightness_json(args) -> None:
    result = assess_tightness(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
