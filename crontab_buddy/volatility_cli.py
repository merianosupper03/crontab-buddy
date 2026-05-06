"""CLI commands for volatility assessment."""

import json
from crontab_buddy.volatility import assess_volatility, batch_volatility


def cmd_volatility_check(args):
    """Print volatility report for a single expression."""
    result = assess_volatility(args.expression)
    if not result.valid:
        print(f"[error] {result.error}")
        return
    print(f"Expression : {result.expression}")
    print(f"Level      : {result.level}")
    print(f"Score      : {result.score:.4f}")
    print(f"Interval   : {result.interval_seconds}s")
    print(f"Description: {result.description}")


def cmd_volatility_level(args):
    """Print only the volatility level."""
    result = assess_volatility(args.expression)
    if not result.valid:
        print(f"[error] {result.error}")
        return
    print(result.level)


def cmd_volatility_score(args):
    """Print only the volatility score."""
    result = assess_volatility(args.expression)
    if not result.valid:
        print(f"[error] {result.error}")
        return
    print(f"{result.score:.4f}")


def cmd_volatility_batch(args):
    """Print volatility levels for multiple expressions."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_volatility(expressions)
    for r in results:
        status = r.level if r.valid else f"error: {r.error}"
        print(f"{r.expression:<30} {status}")


def cmd_volatility_json(args):
    """Output volatility result as JSON."""
    result = assess_volatility(args.expression)
    print(json.dumps({
        "expression": result.expression,
        "level": result.level,
        "score": result.score,
        "interval_seconds": result.interval_seconds,
        "description": result.description,
        "valid": result.valid,
        "error": result.error,
    }, indent=2))
