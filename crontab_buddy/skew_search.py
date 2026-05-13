"""Search history and favorites by skew characteristics."""
from typing import List, Dict, Any
from crontab_buddy.skew import assess_skew
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites

try:
    from crontab_buddy.humanizer import humanize
except Exception:  # pragma: no cover
    humanize = None  # type: ignore


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(expression) if humanize else expression
    except Exception:
        return expression


def search_history_by_skew(label: str) -> List[Dict[str, Any]]:
    """Return history entries whose skew label matches the given label."""
    label = label.lower()
    results = []
    seen = set()
    for entry in get_history():
        expr = entry if isinstance(entry, str) else entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = assess_skew(expr)
        if r.label == label and not r.error:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": r.score,
                "label": r.label,
                "source": "history",
            })
    return results


def search_favorites_by_skew(label: str) -> List[Dict[str, Any]]:
    """Return favorites whose skew label matches the given label."""
    label = label.lower()
    results = []
    for name, expr in list_favorites():
        r = assess_skew(expr)
        if r.label == label and not r.error:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": r.score,
                "label": r.label,
                "source": "favorites",
            })
    return results


def search_above_score(threshold: float) -> List[Dict[str, Any]]:
    """Return history entries with skew score above the given threshold."""
    results = []
    seen = set()
    for entry in get_history():
        expr = entry if isinstance(entry, str) else entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = assess_skew(expr)
        if not r.error and r.score >= threshold:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": r.score,
                "label": r.label,
            })
    return sorted(results, key=lambda x: x["score"], reverse=True)
