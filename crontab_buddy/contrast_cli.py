"""CLI commands for the contrast module."""
from __future__ import annotations
import json
from typing import List

from crontab_buddy.contrast import assess_contrast


def cmd_contrast_check(args) -> None:
    """Print a full contrast report for *expression* vs *peers*."""
    peers: List[str] = args.peers or []
    result = assess_contrast(args.expression, peers)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    print(f"Shared     : {result.shared_minutes} / {result.total_minutes} firing slots")
    print(f"Peers      : {len(peers)}")


def cmd_contrast_score(args) -> None:
    """Print only the numeric contrast score."""
    peers: List[str] = args.peers or []
    result = assess_contrast(args.expression, peers)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_contrast_grade(args) -> None:
    """Print only the contrast grade label."""
    peers: List[str] = args.peers or []
    result = assess_contrast(args.expression, peers)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_contrast_batch(args) -> None:
    """Assess contrast for multiple expressions against the same peer list."""
    peers: List[str] = args.peers or []
    expressions: List[str] = args.expressions or []
    for expr in expressions:
        result = assess_contrast(expr, peers)
        if result.error:
            print(f"{expr!r:40s}  error: {result.error}")
        else:
            print(f"{expr!r:40s}  {result.grade:12s}  {result.score:.4f}")


def cmd_contrast_json(args) -> None:
    """Output the contrast result as JSON."""
    peers: List[str] = args.peers or []
    result = assess_contrast(args.expression, peers)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "shared_minutes": result.shared_minutes,
        "total_minutes": result.total_minutes,
    }
    if result.error:
        data["error"] = result.error
    print(json.dumps(data, indent=2))
