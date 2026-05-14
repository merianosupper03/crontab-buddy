"""Search history/favorites by fuzziness grade or score threshold."""

from crontab_buddy.fuzziness import assess_fuzziness
from crontab_buddy.history import get_history
from crontab_buddy.favorites import list_favorites

try:
    from crontab_buddy.humanizer import humanize
except Exception:  # pragma: no cover
    def humanize(expr):
        return ""


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(expression)
    except Exception:
        return ""


def search_history_by_fuzziness(grade: str) -> list:
    """Return history entries whose fuzziness grade matches."""
    grade = grade.lower()
    seen = set()
    results = []
    for entry in get_history():
        expr = entry if isinstance(entry, str) else entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = assess_fuzziness(expr)
        if r.grade == grade:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "overall": r.overall,
                "grade": r.grade,
                "source": "history",
            })
    return results


def search_favorites_by_fuzziness(grade: str) -> list:
    """Return favorites whose fuzziness grade matches."""
    grade = grade.lower()
    results = []
    for name, expr in list_favorites().items():
        r = assess_fuzziness(expr)
        if r.grade == grade:
            results.append({
                "name": name,
                "expression": expr,
                "description": _safe_humanize(expr),
                "overall": r.overall,
                "grade": r.grade,
                "source": "favorites",
            })
    return results


def search_above_score(threshold: float) -> list:
    """Return history entries with fuzziness overall score above threshold."""
    seen = set()
    results = []
    for entry in get_history():
        expr = entry if isinstance(entry, str) else entry.get("expression", "")
        if expr in seen:
            continue
        seen.add(expr)
        r = assess_fuzziness(expr)
        if not r.error and r.overall >= threshold:
            results.append({
                "expression": expr,
                "description": _safe_humanize(expr),
                "overall": r.overall,
                "grade": r.grade,
            })
    results.sort(key=lambda x: x["overall"], reverse=True)
    return results
