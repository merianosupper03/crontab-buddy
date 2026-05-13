"""CLI commands for burstiness analysis."""

import json

from crontab_buddy.burstiness import assess_burstiness, batch_burstiness


def cmd_burstiness_check(args) -> None:
    result = assess_burstiness(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Label      : {result.label}")
    if result.intervals:
        preview = result.intervals[:8]
        suffix = "..." if len(result.intervals) > 8 else ""
        print(f"Intervals  : {preview}{suffix}")


def cmd_burstiness_score(args) -> None:
    result = assess_burstiness(args.expression)
    print(result.score)


def cmd_burstiness_label(args) -> None:
    result = assess_burstiness(args.expression)
    print(result.label)


def cmd_burstiness_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_burstiness(expressions)
    for r in results:
        status = r.label if not r.error else f"error: {r.error}"
        print(f"{r.expression:<30} {r.score:.4f}  {status}")


def cmd_burstiness_json(args) -> None:
    result = assess_burstiness(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "label": result.label,
        "intervals": result.intervals,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
