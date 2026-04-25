"""Search utilities for alert configurations."""
from __future__ import annotations
from typing import List
from crontab_buddy.alert import list_alerts
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return ""


def search_alerts(
    query: str,
    path: str | None = None,
) -> List[dict]:
    """Search alerts by expression, description, channel, event, or target."""
    kwargs = {"path": path} if path else {}
    alerts = list_alerts(**kwargs)
    q = query.lower()
    results = []
    for expr, cfg in alerts.items():
        desc = _safe_humanize(expr)
        haystack = " ".join([
            expr,
            desc,
            cfg.get("channel", ""),
            cfg.get("event", ""),
            cfg.get("target", "") or "",
        ]).lower()
        if q in haystack:
            results.append({
                "expression": expr,
                "description": desc,
                "channel": cfg["channel"],
                "event": cfg["event"],
                "target": cfg.get("target"),
            })
    return results
