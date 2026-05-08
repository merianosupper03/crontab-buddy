"""CLI commands for contention analysis."""

import json
from crontab_buddy.contention import assess_contention


def cmd_contention_check(args) -> None:
    result = assess_contention(args.expr_a, args.expr_b)
    print(f"Expression A : {result.expression_a}")
    print(f"Expression B : {result.expression_b}")
    if result.error:
        print(f"Error        : {result.error}")
        return
    print(f"Overlap      : {result.overlap_minutes} minute(s)/day")
    print(f"Score        : {result.score:.4f}")
    print(f"Grade        : {result.grade}")


def cmd_contention_score(args) -> None:
    result = assess_contention(args.expr_a, args.expr_b)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_contention_grade(args) -> None:
    result = assess_contention(args.expr_a, args.expr_b)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_contention_json(args) -> None:
    result = assess_contention(args.expr_a, args.expr_b)
    data = {
        "expression_a": result.expression_a,
        "expression_b": result.expression_b,
        "overlap_minutes": result.overlap_minutes,
        "score": result.score,
        "grade": result.grade,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))


def cmd_contention_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    if len(expressions) < 2:
        print("Need at least two expressions for batch contention analysis.")
        return
    for i in range(len(expressions)):
        for j in range(i + 1, len(expressions)):
            result = assess_contention(expressions[i], expressions[j])
            print(str(result))
