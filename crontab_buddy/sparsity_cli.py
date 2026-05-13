"""CLI commands for sparsity analysis."""

import json

from crontab_buddy.sparsity import assess_sparsity, batch_sparsity


def cmd_sparsity_check(args) -> None:
    """Print a full sparsity report for an expression."""
    result = assess_sparsity(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    print(f"Interval   : {result.interval_seconds:.1f}s")


def cmd_sparsity_score(args) -> None:
    """Print only the sparsity score."""
    result = assess_sparsity(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.score)


def cmd_sparsity_grade(args) -> None:
    """Print only the sparsity grade label."""
    result = assess_sparsity(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.grade)


def cmd_sparsity_batch(args) -> None:
    """Print sparsity grades for multiple expressions."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_sparsity(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  error: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.grade:12s}  score={r.score:.4f}")


def cmd_sparsity_json(args) -> None:
    """Output sparsity result as JSON."""
    result = assess_sparsity(args.expression)
    payload = {
        "expression": result.expression,
        "grade": result.grade,
        "score": result.score,
        "interval_seconds": result.interval_seconds,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
