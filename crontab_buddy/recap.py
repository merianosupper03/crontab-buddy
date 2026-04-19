"""Weekly/daily recap of cron usage from history."""
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict, Any

from crontab_buddy.history import get_history
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except (CronParseError, Exception):
        return "(invalid)"


def recap(days: int = 7, path: str | None = None) -> Dict[str, Any]:
    """Return a recap dict summarising usage over the last `days` days."""
    kwargs = {"path": path} if path else {}
    entries = get_history(**kwargs)
    cutoff = datetime.now() - timedelta(days=days)

    recent: List[str] = []
    for entry in entries:
        ts_str = entry.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str)
        except (ValueError, TypeError):
            continue
        if ts >= cutoff:
            recent.append(entry.get("expression", ""))

    freq: Counter = Counter(recent)
    top = [
        {"expression": expr, "count": count, "description": _safe_humanize(expr)}
        for expr, count in freq.most_common(5)
    ]

    return {
        "days": days,
        "total_uses": len(recent),
        "unique_expressions": len(freq),
        "top": top,
    }


def format_recap(data: Dict[str, Any]) -> str:
    """Return a human-readable recap string."""
    lines = [
        f"Recap — last {data['days']} day(s)",
        f"  Total uses   : {data['total_uses']}",
        f"  Unique exprs : {data['unique_expressions']}",
    ]
    if data["top"]:
        lines.append("  Top expressions:")
        for item in data["top"]:
            lines.append(f"    {item['expression']:20s}  x{item['count']}  {item['description']}")
    else:
        lines.append("  No expressions used in this period.")
    return "\n".join(lines)
