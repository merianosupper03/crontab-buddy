"""Suggest common cron expressions based on plain-English keywords."""

from typing import List, Tuple

# (keywords, cron_expression, label)
_SUGGESTIONS: List[Tuple[List[str], str, str]] = [
    (["every minute", "minutely"], "* * * * *", "Every minute"),
    (["every hour", "hourly"], "0 * * * *", "Every hour"),
    (["every day", "daily", "midnight"], "0 0 * * *", "Every day at midnight"),
    (["every weekday", "weekdays", "monday to friday"], "0 9 * * 1-5", "Weekdays at 9 AM"),
    (["every weekend", "weekends"], "0 10 * * 6,0", "Weekends at 10 AM"),
    (["every week", "weekly"], "0 0 * * 0", "Every Sunday at midnight"),
    (["every month", "monthly"], "0 0 1 * *", "First day of every month"),
    (["every year", "yearly", "annually"], "0 0 1 1 *", "Every January 1st"),
    (["every 5 minutes"], "*/5 * * * *", "Every 5 minutes"),
    (["every 15 minutes", "quarter hour"], "*/15 * * * *", "Every 15 minutes"),
    (["every 30 minutes", "half hour"], "*/30 * * * *", "Every 30 minutes"),
    (["every 6 hours"], "0 */6 * * *", "Every 6 hours"),
    (["twice a day", "twice daily"], "0 8,20 * * *", "Twice a day (8 AM and 8 PM)"),
    (["every night", "nightly"], "0 23 * * *", "Every night at 11 PM"),
    (["every morning"], "0 7 * * *", "Every morning at 7 AM"),
]


def suggest(query: str, max_results: int = 5) -> List[Tuple[str, str]]:
    """Return a list of (cron_expression, label) matching the query.

    Matching is case-insensitive substring search against known keywords.
    """
    q = query.lower().strip()
    results: List[Tuple[str, str]] = []
    seen: set = set()

    for keywords, expr, label in _SUGGESTIONS:
        for kw in keywords:
            if q in kw or kw in q:
                if expr not in seen:
                    results.append((expr, label))
                    seen.add(expr)
                break

    return results[:max_results]


def list_all() -> List[Tuple[str, str]]:
    """Return all built-in suggestions as (cron_expression, label) pairs."""
    return [(expr, label) for _, expr, label in _SUGGESTIONS]
