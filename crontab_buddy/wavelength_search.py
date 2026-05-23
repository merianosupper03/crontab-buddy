"""Search history/favorites by wavelength label or score range."""
from __future__ import annotations
from typing import List, Dict, Any
from crontab_buddy.wavelength import assess_wavelength
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid)"


def search_history_by_wavelength(label: str) -> List[Dict[str, Any]]:
    """Return history entries whose wavelength label matches."""
    seen: set = set()
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = assess_wavelength(expr)
        if r.error:
            continue
        if r.label.lower() == label.lower():
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "period_seconds": r.period_seconds,
                "score": r.score,
                "label": r.label,
                "source": "history",
            })
    return results


def search_favorites_by_wavelength(label: str) -> List[Dict[str, Any]]:
    """Return favorites whose wavelength label matches."""
    results = []
    for name, expr in list_favorites().items():
        r = assess_wavelength(expr)
        if r.error:
            continue
        if r.label.lower() == label.lower():
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "period_seconds": r.period_seconds,
                "score": r.score,
                "label": r.label,
                "source": "favorites",
            })
    return results


def search_above_score(min_score: float) -> List[Dict[str, Any]]:
    """Return history entries with wavelength score >= min_score."""
    seen: set = set()
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = assess_wavelength(expr)
        if r.error:
            continue
        if r.score >= min_score:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": r.score,
                "label": r.label,
                "source": "history",
            })
    return sorted(results, key=lambda x: x["score"], reverse=True)
