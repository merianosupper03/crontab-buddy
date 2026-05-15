"""Search history and favorites by density characteristics."""

from typing import List, Dict, Any

from .density import DensityResult, _safe_parse, compute_density
from .history import get_history
from .favorites import list_favorites


def _safe_humanize(expr: str) -> str:
    try:
        from .humanizer import humanize
        from .parser import CronExpression
        return humanize(CronExpression(expr))
    except Exception:
        return expr


def search_history_by_density(
    label: str,
    window: str = "24h",
    min_fires: int = 0,
) -> List[Dict[str, Any]]:
    """Return history entries whose density label matches and fires >= min_fires."""
    results = []
    seen = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        try:
            result = compute_density([expr], window=window)
            entry_label = result.label.lower()
            if label.lower() not in entry_label:
                continue
            total = result.windows.get(window, 0)
            if total < min_fires:
                continue
            seen.add(expr)
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "label": result.label,
                "fires": total,
                "source": "history",
            })
        except Exception:
            continue
    return results


def search_favorites_by_density(
    label: str,
    window: str = "24h",
    min_fires: int = 0,
) -> List[Dict[str, Any]]:
    """Return favorites whose density label matches and fires >= min_fires."""
    results = []
    for name, expr in list_favorites():
        try:
            result = compute_density([expr], window=window)
            entry_label = result.label.lower()
            if label.lower() not in entry_label:
                continue
            total = result.windows.get(window, 0)
            if total < min_fires:
                continue
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "label": result.label,
                "fires": total,
                "source": "favorites",
            })
        except Exception:
            continue
    return results
