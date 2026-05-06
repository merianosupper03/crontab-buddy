"""CLI commands for reachability analysis."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .reachability import ReachabilityResult, batch_reachability, check_reachability


def _parse_dt(value: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse datetime: {value!r}")


def cmd_reachability_check(args: Any) -> None:
    """Check a single expression for reachability."""
    start = _parse_dt(args.start) if getattr(args, "start", None) else None
    end = _parse_dt(args.end) if getattr(args, "end", None) else None
    result = check_reachability(
        args.expression,
        start=start,
        end=end,
        window_days=getattr(args, "window", 366),
    )
    print(str(result))


def cmd_reachability_batch(args: Any) -> None:
    """Check multiple expressions (space-separated) for reachability."""
    results = batch_reachability(
        args.expressions,
        window_days=getattr(args, "window", 366),
    )
    for r in results:
        print(str(r))
        print()
    reachable = sum(1 for r in results if r.reachable)
    print(f"Summary: {reachable}/{len(results)} reachable")


def cmd_reachability_json(args: Any) -> None:
    """Output reachability result as JSON."""
    result = check_reachability(
        args.expression,
        window_days=getattr(args, "window", 366),
    )
    data = {
        "expression": result.expression,
        "reachable": result.reachable,
        "reason": result.reason,
        "next_occurrences": result.next_occurrences,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
