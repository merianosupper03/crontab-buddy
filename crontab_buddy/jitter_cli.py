"""CLI commands for jitter analysis."""

import json

from crontab_buddy.jitter import assess_jitter, batch_jitter


def cmd_jitter_check(args) -> None:
    """Print a full jitter report for a cron expression."""
    result = assess_jitter(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Label      : {result.label}")
    contributors = ", ".join(result.fields_contributing) if result.fields_contributing else "none"
    print(f"Contributors: {contributors}")


def cmd_jitter_score(args) -> None:
    """Print only the numeric jitter score."""
    result = assess_jitter(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(f"{result.score:.4f}")


def cmd_jitter_label(args) -> None:
    """Print only the jitter label."""
    result = assess_jitter(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.label)


def cmd_jitter_batch(args) -> None:
    """Print jitter scores for multiple expressions."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_jitter(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  error: {r.error}")
        else:
            print(f"{r.expression!r:30s}  score={r.score:.4f}  label={r.label}")


def cmd_jitter_json(args) -> None:
    """Output jitter result as JSON."""
    result = assess_jitter(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "label": result.label,
        "fields_contributing": result.fields_contributing,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
