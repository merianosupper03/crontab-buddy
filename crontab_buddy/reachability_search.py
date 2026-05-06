"""Search utilities that filter stored expressions by reachability."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from .favorites import list_favorites
from .history import get_history
from .reachability import ReachabilityResult, check_reachability


def _label(source: str, name: Optional[str] = None) -> str:
    if name:
        return f"[{source}:{name}]"
    return f"[{source}]"


def search_reachable_history(
    window_days: int = 366,
    after: Optional[datetime] = None,
) -> List[ReachabilityResult]:
    """Return reachability results for all history entries that are reachable."""
    results = []
    for entry in get_history():
        expr = entry if isinstance(entry, str) else entry.get("expression", "")
        r = check_reachability(expr, start=after, window_days=window_days)
        if r.reachable:
            results.append(r)
    return results


def search_unreachable_favorites(
    window_days: int = 366,
) -> List[ReachabilityResult]:
    """Return reachability results for favorites that will NOT fire in the window."""
    results = []
    for name, expr in list_favorites().items():
        r = check_reachability(expr, window_days=window_days)
        if not r.reachable:
            results.append(r)
    return results


def reachability_summary(
    expressions: List[str],
    window_days: int = 366,
) -> dict:
    """Return a dict summary with counts of reachable vs unreachable."""
    results = [check_reachability(e, window_days=window_days) for e in expressions]
    reachable = [r for r in results if r.reachable]
    unreachable = [r for r in results if not r.reachable]
    return {
        "total": len(results),
        "reachable": len(reachable),
        "unreachable": len(unreachable),
        "results": results,
    }
