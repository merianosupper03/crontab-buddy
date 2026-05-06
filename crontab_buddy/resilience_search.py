"""Search utilities for resilience scores."""

from typing import List, Dict, Any
from crontab_buddy.resilience import score_resilience, ResilienceResult


def _safe_humanize(expression: str) -> str:
    try:
        from crontab_buddy.humanizer import humanize
        from crontab_buddy.parser import CronExpression
        return humanize(CronExpression(expression))
    except Exception:
        return expression


def search_by_grade(
    expressions: List[str],
    grade: str,
    **kwargs,
) -> List[Dict[str, Any]]:
    """Return expressions whose resilience grade matches the given grade."""
    grade = grade.upper()
    results = []
    for expr in expressions:
        try:
            r: ResilienceResult = score_resilience(expr, **kwargs)
        except Exception:
            continue
        if r.grade == grade:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": r.score,
                "grade": r.grade,
            })
    return results


def search_below_score(
    expressions: List[str],
    threshold: int,
    **kwargs,
) -> List[Dict[str, Any]]:
    """Return expressions with a resilience score below the given threshold."""
    results = []
    for expr in expressions:
        try:
            r: ResilienceResult = score_resilience(expr, **kwargs)
        except Exception:
            continue
        if r.score < threshold:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "score": r.score,
                "grade": r.grade,
            })
    return results
