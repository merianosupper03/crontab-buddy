"""CLI commands for gradient analysis."""

import json
from crontab_buddy.gradient import compute_gradient


def cmd_gradient_check(args, print_fn=print):
    result = compute_gradient(args.expression)
    print_fn(f"Expression : {result.expression}")
    print_fn(f"Gradient   : {result.label}")
    print_fn(f"Score      : {result.score:.4f}")
    if result.error:
        print_fn(f"Error      : {result.error}")
    elif result.deltas:
        print_fn(f"Gaps (min) : {result.deltas}")


def cmd_gradient_score(args, print_fn=print):
    result = compute_gradient(args.expression)
    print_fn(str(result.score))


def cmd_gradient_label(args, print_fn=print):
    result = compute_gradient(args.expression)
    print_fn(result.label)


def cmd_gradient_batch(args, print_fn=print):
    expressions = [e.strip() for e in args.expressions if e.strip()]
    for expr in expressions:
        result = compute_gradient(expr)
        print_fn(f"{expr:<30} {result.label:<10} {result.score:.4f}")


def cmd_gradient_json(args, print_fn=print):
    result = compute_gradient(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "label": result.label,
        "deltas": result.deltas,
        "error": result.error,
    }
    print_fn(json.dumps(data, indent=2))
