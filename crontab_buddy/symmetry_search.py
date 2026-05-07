from crontab_buddy.symmetry import check_symmetry
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites


def _safe_humanize(expr: str) -> str:
    try:
        from crontab_buddy.humanizer import humanize
        from crontab_buddy.parser import CronExpression
        return humanize(CronExpression(expr))
    except Exception:
        return ""


def find_symmetric_in_history(expr: str, min_score: float = 0.8):
    """
    Search history for expressions that are highly symmetric with *expr*.
    Returns a list of dicts with keys: expression, description, score.
    """
    results = []
    seen = set()
    for entry in get_history():
        candidate = entry.get("expression", "")
        if candidate == expr or candidate in seen:
            continue
        seen.add(candidate)
        result = check_symmetry(expr, candidate)
        if result.score >= min_score:
            results.append({
                "expression": candidate,
                "description": _safe_humanize(candidate),
                "score": result.score,
                "label": result.label,
            })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def find_symmetric_in_favorites(expr: str, min_score: float = 0.8):
    """
    Search saved favorites for expressions symmetric with *expr*.
    """
    results = []
    for name, candidate in list_favorites():
        if candidate == expr:
            continue
        result = check_symmetry(expr, candidate)
        if result.score >= min_score:
            results.append({
                "name": name,
                "expression": candidate,
                "description": _safe_humanize(candidate),
                "score": result.score,
                "label": result.label,
            })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results
