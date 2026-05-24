"""CLI commands for churn analysis."""
from __future__ import annotations
import json
from typing import List

from crontab_buddy.churn import assess_churn, batch_churn


def cmd_churn_check(args) -> None:
    """Print a full churn report for an expression against optional peers."""
    peers: List[str] = getattr(args, "peers", []) or []
    result = assess_churn(args.expression, peers)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.3f}")
    print(f"Grade      : {result.grade}")
    print(f"Unique peers     : {result.unique_peers}")
    print(f"Overlapping peers: {result.overlapping_peers}")


def cmd_churn_score(args) -> None:
    """Print only the numeric churn score."""
    peers: List[str] = getattr(args, "peers", []) or []
    result = assess_churn(args.expression, peers)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.score)


def cmd_churn_grade(args) -> None:
    """Print only the churn grade label."""
    peers: List[str] = getattr(args, "peers", []) or []
    result = assess_churn(args.expression, peers)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.grade)


def cmd_churn_batch(args) -> None:
    """Run batch churn across a list of expressions."""
    expressions: List[str] = args.expressions or []
    results = batch_churn(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  ERROR: {r.error}")
        else:
            print(f"{r.expression!r:40s}  score={r.score:.3f}  grade={r.grade}")


def cmd_churn_json(args) -> None:
    """Emit churn result as JSON."""
    peers: List[str] = getattr(args, "peers", []) or []
    result = assess_churn(args.expression, peers)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "unique_peers": result.unique_peers,
        "overlapping_peers": result.overlapping_peers,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
