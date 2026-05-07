"""CLI commands for momentum analysis."""

from __future__ import annotations

import json

from crontab_buddy.momentum import compute_momentum, batch_momentum


def cmd_momentum_check(args) -> None:
    """Print full momentum report for an expression."""
    result = compute_momentum(args.expression)
    print(result)


def cmd_momentum_score(args) -> None:
    """Print only the momentum score."""
    result = compute_momentum(args.expression)
    print(f"{result.score:.4f}")


def cmd_momentum_level(args) -> None:
    """Print only the momentum level label."""
    result = compute_momentum(args.expression)
    print(result.level)


def cmd_momentum_batch(args) -> None:
    """Print momentum for multiple expressions."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_momentum(expressions)
    for r in results:
        print(f"{r.expression:<25} score={r.score:.2f}  level={r.level}")


def cmd_momentum_json(args) -> None:
    """Print momentum result as JSON."""
    result = compute_momentum(args.expression)
    data = {
        "expression": result.expression,
        "total_uses": result.total_uses,
        "recent_uses": result.recent_uses,
        "score": result.score,
        "level": result.level,
    }
    print(json.dumps(data, indent=2))
