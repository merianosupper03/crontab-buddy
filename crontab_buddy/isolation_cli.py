"""CLI commands for cron expression isolation scoring."""
from __future__ import annotations

import json
from typing import List

from crontab_buddy.isolation import assess_isolation


def _peers_from_args(args) -> List[str]:
    return list(args.peers) if getattr(args, "peers", None) else []


def cmd_isolation_check(args, out=print) -> None:
    """Print a human-readable isolation report."""
    peers = _peers_from_args(args)
    result = assess_isolation(args.expression, peers)
    out(f"Expression : {result.expression}")
    if result.error:
        out(f"Error      : {result.error}")
        return
    out(f"Score      : {result.score:.4f}")
    out(f"Grade      : {result.grade}")
    out(f"Neighbours : {result.neighbours}")


def cmd_isolation_score(args, out=print) -> None:
    """Print only the numeric isolation score."""
    peers = _peers_from_args(args)
    result = assess_isolation(args.expression, peers)
    out(str(result.score))


def cmd_isolation_grade(args, out=print) -> None:
    """Print only the isolation grade label."""
    peers = _peers_from_args(args)
    result = assess_isolation(args.expression, peers)
    out(result.grade)


def cmd_isolation_batch(args, out=print) -> None:
    """Assess isolation for each expression in args.expressions against the others."""
    expressions: List[str] = list(args.expressions)
    for expr in expressions:
        peers = [e for e in expressions if e != expr]
        result = assess_isolation(expr, peers)
        if result.error:
            out(f"{expr}  ->  ERROR: {result.error}")
        else:
            out(f"{expr}  ->  {result.grade} (score={result.score:.4f}, neighbours={result.neighbours})")


def cmd_isolation_json(args, out=print) -> None:
    """Emit isolation result as JSON."""
    peers = _peers_from_args(args)
    result = assess_isolation(args.expression, peers)
    out(json.dumps({
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "neighbours": result.neighbours,
        "error": result.error,
    }))
