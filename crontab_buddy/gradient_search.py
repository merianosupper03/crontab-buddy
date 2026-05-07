"""Search history and favorites by gradient label or score threshold."""

from typing import List, Dict, Any
from crontab_buddy.gradient import compute_gradient
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites


def _safe_humanize(expression: str) -> str:
    try:
        from crontab_buddy.humanizer import humanize
        from crontab_buddy.parser import CronExpression
        return humanize(CronExpression(expression))
    except Exception:
        return "(invalid)"


def search_history_by_gradient(label: str) -> List[Dict[str, Any]]:
    """Return history entries whose gradient label matches."""
    label = label.lower()
    results = []
    seen = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        result = compute_gradient(expr)
        if result.label == label:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": result.score,
                "label": result.label,
                "source": "history",
            })
    return results


def search_favorites_by_gradient(label: str) -> List[Dict[str, Any]]:
    """Return favorites whose gradient label matches."""
    label = label.lower()
    results = []
    for name, expr in list_favorites():
        result = compute_gradient(expr)
        if result.label == label:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": result.score,
                "label": result.label,
                "source": "favorites",
            })
    return results


def search_above_score(threshold: float) -> List[Dict[str, Any]]:
    """Return all history entries with gradient score above threshold."""
    results = []
    seen = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        result = compute_gradient(expr)
        if result.score >= threshold:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": result.score,
                "label": result.label,
            })
    return sorted(results, key=lambda x: x["score"], reverse=True)
