"""Search trigger rules by event type or condition keyword."""

from typing import List, Optional
from crontab_buddy.trigger import list_triggers
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def search_triggers(
    query: str,
    event_filter: Optional[str] = None,
    path: Optional[str] = None,
) -> List[dict]:
    """Search trigger rules matching a query string and optional event type.

    Args:
        query: substring to match against expression or condition.
        event_filter: if given, only return rules with this event type.
        path: optional custom storage path.

    Returns:
        List of matching trigger dicts with added 'description' key.
    """
    kwargs = {} if path is None else {"path": path}
    rules = list_triggers(**kwargs)
    results = []
    q = query.lower()
    for rule in rules:
        if event_filter and rule["event"] != event_filter:
            continue
        expr = rule["expression"]
        cond = (rule.get("condition") or "").lower()
        if q in expr.lower() or q in cond or q in rule["event"]:
            results.append({
                **rule,
                "description": _safe_humanize(expr),
            })
    return results
