"""Recurrence pattern analysis for cron expressions."""

from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError


RECURRENCE_PATTERNS = {
    "yearly": ("0", "0", "1", "1", "*"),
    "monthly": ("0", "0", "1", "*", "*"),
    "weekly": ("0", "0", "*", "*", "0"),
    "daily": ("0", "0", "*", "*", "*"),
    "hourly": ("0", "*", "*", "*", "*"),
    "every_minute": ("*", "*", "*", "*", "*"),
}


def detect_recurrence(expression: str) -> Optional[str]:
    """Return a named recurrence pattern for a cron expression, or None."""
    try:
        expr = CronExpression(expression)
    except CronParseError:
        return None

    fields = (expr.minute, expr.hour, expr.dom, expr.month, expr.dow)
    for name, pattern in RECURRENCE_PATTERNS.items():
        if fields == pattern:
            return name
    return None


def recurrence_interval_seconds(expression: str) -> Optional[int]:
    """Estimate the recurrence interval in seconds for known patterns."""
    pattern = detect_recurrence(expression)
    intervals = {
        "every_minute": 60,
        "hourly": 3600,
        "daily": 86400,
        "weekly": 604800,
        "monthly": 2592000,
        "yearly": 31536000,
    }
    return intervals.get(pattern) if pattern else None


def is_high_frequency(expression: str, threshold_seconds: int = 300) -> bool:
    """Return True if the expression fires more often than threshold_seconds."""
    interval = recurrence_interval_seconds(expression)
    if interval is None:
        return False
    return interval < threshold_seconds


def describe_recurrence(expression: str) -> str:
    """Return a human-readable recurrence label for the expression."""
    pattern = detect_recurrence(expression)
    labels = {
        "every_minute": "every minute",
        "hourly": "once per hour",
        "daily": "once per day",
        "weekly": "once per week",
        "monthly": "once per month",
        "yearly": "once per year",
    }
    return labels.get(pattern, "custom schedule") if pattern else "custom schedule"
