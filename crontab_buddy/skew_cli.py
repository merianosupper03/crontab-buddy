"""CLI commands for skew analysis."""
import json
from crontab_buddy.skew import assess_skew, batch_skew


def cmd_skew_check(args) -> None:
    result = assess_skew(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Label      : {result.label}")
    print(f"Score      : {result.score:.4f}")
    print(f"Morning AM : {result.morning_share:.0%}")
    print(f"Afternoon PM: {result.afternoon_share:.0%}")


def cmd_skew_score(args) -> None:
    result = assess_skew(args.expression)
    print(f"{result.score:.4f}")


def cmd_skew_label(args) -> None:
    result = assess_skew(args.expression)
    print(result.label)


def cmd_skew_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions.split(",") if e.strip()]
    results = batch_skew(expressions)
    for r in results:
        status = r.error if r.error else f"{r.label} (score={r.score:.2f})"
        print(f"{r.expression:30s}  {status}")


def cmd_skew_json(args) -> None:
    result = assess_skew(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "label": result.label,
        "morning_share": result.morning_share,
        "afternoon_share": result.afternoon_share,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
