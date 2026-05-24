"""coverage_score_search.py — search history/favorites by coverage score."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from crontab_buddy.coverage_score import compute_coverage_score
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites

try:
    from crontab_buddy.humanizer import humanize
except Exception:  # pragma: no cover
    humanize = None  # type: ignore


def _safe_humanize(expression: str) -> str:
    try:
        if humanize:
            return humanize(expression)
    except Exception:
        pass
    return ""


def search_history_by_coverage_score(
    min_score: float = 0.0,
    max_score: float = 1.0,
    path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return history entries whose coverage score falls within [min_score, max_score]."""
    entries = get_history(path=path) if path else get_history()
    seen = set()
    results = []
    for entry in entries:
        expr = entry if isinstance(entry, str) else entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = compute_coverage_score(expr)
        if r.error:
            continue
        if min_score <= r.score <= max_score:
            results.append({
                "expression": expr,
                "score": r.score,
                "grade": r.grade,
                "description": _safe_humanize(expr),
                "source": "history",
            })
    return results


def search_favorites_by_coverage_score(
    min_score: float = 0.0,
    max_score: float = 1.0,
    path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return favorites whose coverage score falls within [min_score, max_score]."""
    favs = list_favorites(path=path) if path else list_favorites()
    results = []
    for name, expr in favs.items():
        r = compute_coverage_score(expr)
        if r.error:
            continue
        if min_score <= r.score <= max_score:
            results.append({
                "name": name,
                "expression": expr,
                "score": r.score,
                "grade": r.grade,
                "description": _safe_humanize(expr),
                "source": "favorites",
            })
    return results
