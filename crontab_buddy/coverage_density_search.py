"""Search history and favorites by coverage density grade/score."""

from typing import List, Dict, Any

from .favorites import list_favorites
from .history import get_history
from .humanizer import humanize
from .parser import CronExpression, CronParseError
from .coverage_density import assess_coverage_density


def _safe_humanize(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except (CronParseError, Exception):
        return ""


def search_history_by_coverage_density(
    min_score: float = 0.0,
    grade: str | None = None,
) -> List[Dict[str, Any]]:
    """Return history entries whose coverage density meets the criteria."""
    results: List[Dict[str, Any]] = []
    seen: set = set()
    for entry in get_history():
        expr = entry if isinstance(entry, str) else entry.get("expression", "")
        if not expr or expr in seen:
            continue
        seen.add(expr)
        result = assess_coverage_density([expr])
        if result.error:
            continue
        if result.score < min_score:
            continue
        if grade and result.grade.lower() != grade.lower():
            continue
        results.append({
            "expression": expr,
            "description": _safe_humanize(expr),
            "score": result.score,
            "grade": result.grade,
            "source": "history",
        })
    return results


def search_favorites_by_coverage_density(
    min_score: float = 0.0,
    grade: str | None = None,
) -> List[Dict[str, Any]]:
    """Return favorites whose coverage density meets the criteria."""
    results: List[Dict[str, Any]] = []
    for name, expr in list_favorites().items():
        result = assess_coverage_density([expr])
        if result.error:
            continue
        if result.score < min_score:
            continue
        if grade and result.grade.lower() != grade.lower():
            continue
        results.append({
            "name": name,
            "expression": expr,
            "description": _safe_humanize(expr),
            "score": result.score,
            "grade": result.grade,
            "source": "favorites",
        })
    return results
