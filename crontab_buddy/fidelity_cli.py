"""CLI commands for fidelity scoring."""

import json
from crontab_buddy.fidelity import assess_fidelity


def cmd_fidelity_check(args) -> None:
    """Print a human-readable fidelity report for an expression."""
    result = assess_fidelity(args.expression)
    print(result)


def cmd_fidelity_score(args) -> None:
    """Print only the numeric fidelity score."""
    result = assess_fidelity(args.expression)
    print(f"{result.score:.4f}")


def cmd_fidelity_level(args) -> None:
    """Print only the fidelity level label."""
    result = assess_fidelity(args.expression)
    print(result.level)


def cmd_fidelity_batch(args) -> None:
    """Check fidelity for multiple space-separated expressions."""
    expressions = args.expressions
    for expr in expressions:
        result = assess_fidelity(expr)
        print(f"{expr!r:30s}  {result.level:12s}  {result.score:.4f}")


def cmd_fidelity_json(args) -> None:
    """Output fidelity result as JSON."""
    result = assess_fidelity(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "level": result.level,
        "details": result.details,
    }
    print(json.dumps(payload, indent=2))
