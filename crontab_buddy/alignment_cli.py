"""CLI commands for alignment analysis."""

import json
from crontab_buddy.alignment import assess_alignment


def cmd_alignment_check(args):
    """Print full alignment report for a cron expression."""
    result = assess_alignment(args.expression)
    if result.error:
        print(f"[error] {result.error}")
        return
    print(f"Expression : {result.expression}")
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.2f}")
    patterns = ", ".join(result.matched_patterns) if result.matched_patterns else "(none)"
    print(f"Patterns   : {patterns}")


def cmd_alignment_grade(args):
    """Print only the alignment grade for a cron expression."""
    result = assess_alignment(args.expression)
    if result.error:
        print(f"[error] {result.error}")
        return
    print(result.grade)


def cmd_alignment_score(args):
    """Print only the numeric alignment score."""
    result = assess_alignment(args.expression)
    if result.error:
        print(f"[error] {result.error}")
        return
    print(f"{result.score:.4f}")


def cmd_alignment_batch(args):
    """Check alignment for multiple space-separated expressions."""
    expressions = args.expressions
    for expr in expressions:
        result = assess_alignment(expr)
        if result.error:
            print(f"{expr!r:30s}  ERROR: {result.error}")
        else:
            print(f"{expr!r:30s}  {result.grade:20s}  score={result.score:.2f}")


def cmd_alignment_json(args):
    """Output alignment result as JSON."""
    result = assess_alignment(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "matched_patterns": result.matched_patterns,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
