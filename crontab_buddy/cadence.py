"""Cadence tracking: detect and describe the rhythm of cron expression usage."""

from typing import Optional
from crontab_buddy.recurrence import detect_recurrence, recurrence_interval_seconds


CADENCE_LEVELS = {
    "burst": (0, 60),
    "frequent": (61, 3600),
    "regular": (3601, 86400),
    "infrequent": (86401, 604800),
    "rare": (604801, None),
}


def classify_cadence(expression: str) -> str:
    """Return a cadence level string for the given cron expression."""
    try:
        interval = recurrence_interval_seconds(expression)
    except Exception:
        return "unknown"

    if interval is None:
        return "unknown"

    for level, (low, high) in CADENCE_LEVELS.items():
        if high is None:
            if interval > low:
                return level
        elif low <= interval <= high:
            return level

    return "unknown"


def cadence_summary(expression: str) -> dict:
    """Return a dict with cadence level, interval, and recurrence type."""
    try:
        interval = recurrence_interval_seconds(expression)
        recurrence = detect_recurrence(expression)
    except Exception:
        return {"expression": expression, "cadence": "unknown", "interval_seconds": None, "recurrence": "unknown"}

    level = classify_cadence(expression)
    return {
        "expression": expression,
        "cadence": level,
        "interval_seconds": interval,
        "recurrence": recurrence,
    }


def format_cadence(expression: str) -> str:
    """Return a human-readable cadence description."""
    summary = cadence_summary(expression)
    cadence = summary["cadence"]
    recurrence = summary["recurrence"]
    interval = summary["interval_seconds"]

    if cadence == "unknown":
        return f"{expression}: cadence unknown"

    interval_str = f"{interval}s" if interval is not None else "?"
    return f"{expression}: {cadence} cadence ({recurrence}, ~{interval_str} interval)"
