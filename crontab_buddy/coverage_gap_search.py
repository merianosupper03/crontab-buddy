"""Search history and favorites for expressions with coverage gaps."""

from typing import List, Dict, Any

from crontab_buddy.coverage_gap import find_coverage_gaps
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites

try:
    from crontab_buddy.humanizer import humanize
except Exception:
    humanize = None


def _safe_humanize(expression: str) -> str:
    try:
        if humanize:
            return humanize(expression)
    except Exception:
        pass
    return ""


def search_history_with_gaps(
    min_gap_hours: int = 1,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """Return history entries whose expressions have at least min_gap_hours uncovered."""
    seen = set()
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        gaps = find_coverage_gaps([expr])
        if len(gaps) >= min_gap_hours:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "gap_hours": gaps,
                "gap_count": len(gaps),
                "source": "history",
            })
        if len(results) >= max_results:
            break
    return results


def search_favorites_with_gaps(
    min_gap_hours: int = 1,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """Return favorites whose expressions have at least min_gap_hours uncovered."""
    results = []
    for name, expr in list_favorites().items():
        gaps = find_coverage_gaps([expr])
        if len(gaps) >= min_gap_hours:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "gap_hours": gaps,
                "gap_count": len(gaps),
                "source": "favorites",
            })
        if len(results) >= max_results:
            break
    return results


def search_all_with_gaps(
    min_gap_hours: int = 1,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """Combine history and favorites gap search results."""
    combined = search_history_with_gaps(min_gap_hours, max_results)
    seen = {r["expression"] for r in combined}
    for item in search_favorites_with_gaps(min_gap_hours, max_results):
        if item["expression"] not in seen:
            combined.append(item)
            seen.add(item["expression"])
    return combined[:max_results]
