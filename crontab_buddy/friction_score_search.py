"""Search history and favorites by friction score."""

from __future__ import annotations
from typing import List, Dict, Any

from crontab_buddy.friction_score import compute_friction_score
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites

try:
    from crontab_buddy.humanizer import humanize
    from crontab_buddy.parser import CronExpression, CronParseError
except Exception:  # pragma: no cover
    humanize = None  # type: ignore


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))  # type: ignore
    except Exception:
        return ""


def search_history_by_friction_score(
    min_score: float = 0.0,
    max_score: float = 1.0,
) -> List[Dict[str, Any]]:
    """Return history entries whose friction score falls within [min_score, max_score]."""
    results = []
    seen = set()
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = compute_friction_score(expr)
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
    results.sort(key=lambda x: x["score"])
    return results


def search_favorites_by_friction_score(
    min_score: float = 0.0,
    max_score: float = 1.0,
) -> List[Dict[str, Any]]:
    """Return favorites whose friction score falls within [min_score, max_score]."""
    results = []
    for name, expr in list_favorites():
        r = compute_friction_score(expr)
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
    results.sort(key=lambda x: x["score"])
    return results


def search_above_score(threshold: float) -> List[Dict[str, Any]]:
    """Return all (history + favorites) entries with friction score above threshold."""
    hist = search_history_by_friction_score(min_score=threshold)
    favs = search_favorites_by_friction_score(min_score=threshold)
    combined = {r["expression"]: r for r in hist}
    for r in favs:
        combined.setdefault(r["expression"], r)
    return sorted(combined.values(), key=lambda x: x["score"], reverse=True)
