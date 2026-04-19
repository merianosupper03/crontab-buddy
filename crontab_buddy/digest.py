"""Weekly/daily digest summary of cron expression activity."""
from datetime import datetime, timedelta
from typing import Optional
from crontab_buddy.history import get_history
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except (CronParseError, Exception):
        return "(invalid expression)"


def _since(days: int) -> datetime:
    return datetime.utcnow() - timedelta(days=days)


def build_digest(days: int = 7, path: Optional[str] = None) -> dict:
    """Return a digest dict summarising activity over the last `days` days."""
    kwargs = {"path": path} if path else {}
    entries = get_history(**kwargs)

    cutoff = _since(days)
    recent = []
    for e in entries:
        ts = e.get("timestamp")
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                if dt >= cutoff:
                    recent.append(e)
            except ValueError:
                pass

    freq: dict[str, int] = {}
    for e in recent:
        expr = e.get("expression", "")
        freq[expr] = freq.get(expr, 0) + 1

    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
    top_annotated = [
        {"expression": expr, "count": count, "description": _safe_humanize(expr)}
        for expr, count in top
    ]

    return {
        "period_days": days,
        "total_uses": len(recent),
        "unique_expressions": len(freq),
        "top_expressions": top_annotated,
    }


def format_digest(digest: dict) -> str:
    """Return a human-readable string for the digest."""
    lines = [
        f"=== Crontab Buddy Digest (last {digest['period_days']} days) ===",
        f"Total uses    : {digest['total_uses']}",
        f"Unique exprs  : {digest['unique_expressions']}",
        "",
        "Top expressions:",
    ]
    if not digest["top_expressions"]:
        lines.append("  (none)")
    else:
        for i, item in enumerate(digest["top_expressions"], 1):
            lines.append(f"  {i}. {item['expression']}  [{item['count']}x]")
            lines.append(f"     {item['description']}")
    return "\n".join(lines)
