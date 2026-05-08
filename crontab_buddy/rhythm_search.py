"""Search history and favorites by rhythm level or score threshold."""

from typing import List, Dict, Any

from crontab_buddy.rhythm import assess_rhythm
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites

try:
    from crontab_buddy.humanizer import humanize
except Exception:
    humanize = None  # type: ignore


def _safe_humanize(expression: str) -> str:
    try:
        if humanize:
            return humanize(expression)
    except Exception:
        pass
    return ""


def search_history_by_rhythm(
    level: str,
    *,
    min_score: float = 0.0,
) -> List[Dict[str, Any]]:
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        r = assess_rhythm(expr)
        if r.error:
            continue
        if r.level == level and r.score >= min_score:
            results.append({
                "expression": expr,
                "level": r.level,
                "score": r.score,
                "description": _safe_humanize(expr),
            })
    return results


def search_favorites_by_rhythm(
    level: str,
    *,
    min_score: float = 0.0,
) -> List[Dict[str, Any]]:
    results = []
    for name, expr in list_favorites():
        r = assess_rhythm(expr)
        if r.error:
            continue
        if r.level == level and r.score >= min_score:
            results.append({
                "name": name,
                "expression": expr,
                "level": r.level,
                "score": r.score,
                "description": _safe_humanize(expr),
            })
    return results


def search_above_score(threshold: float) -> List[Dict[str, Any]]:
    seen = set()
    results = []
    for entry in get_history():
        expr = entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = assess_rhythm(expr)
        if r.error or r.score < threshold:
            continue
        results.append({
            "expression": expr,
            "level": r.level,
            "score": r.score,
            "description": _safe_humanize(expr),
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)
