"""Usage statistics for cron expressions stored in history."""

from collections import Counter
from typing import Dict, List

from crontab_buddy.history import get_history
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_parse(expr: str):
    try:
        return CronExpression(expr)
    except CronParseError:
        return None


def expression_frequency(history_path=None) -> List[Dict]:
    """Return expressions sorted by how often they appear in history."""
    kwargs = {"path": history_path} if history_path else {}
    entries = get_history(**kwargs)
    counts = Counter(entries)
    result = []
    for expr, count in counts.most_common():
        parsed = _safe_parse(expr)
        result.append({
            "expression": expr,
            "count": count,
            "description": humanize(parsed) if parsed else "(invalid)",
        })
    return result


def field_distribution(history_path=None) -> Dict[str, Counter]:
    """Return Counter per field showing which values appear most."""
    kwargs = {"path": history_path} if history_path else {}
    entries = get_history(**kwargs)
    fields = ["minute", "hour", "dom", "month", "dow"]
    dist: Dict[str, Counter] = {f: Counter() for f in fields}
    for expr in entries:
        parsed = _safe_parse(expr)
        if parsed is None:
            continue
        for field, value in zip(fields, [
            parsed.minute, parsed.hour, parsed.dom, parsed.month, parsed.dow
        ]):
            dist[field][value] += 1
    return dist


def summary(history_path=None) -> Dict:
    """High-level summary of history usage."""
    kwargs = {"path": history_path} if history_path else {}
    entries = get_history(**kwargs)
    unique = set(entries)
    freq = expression_frequency(**kwargs)
    most_used = freq[0] if freq else None
    return {
        "total_entries": len(entries),
        "unique_expressions": len(unique),
        "most_used": most_used,
    }
