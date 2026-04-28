"""Maturity scoring for cron expressions based on configuration richness."""

from typing import Dict, List

from crontab_buddy import (
    tags, notes, favorites, lock, priority, ownership, retry, timeout,
    healthcheck, alert, notify, metadata
)

MATURITY_CHECKS: List[Dict] = [
    {"label": "has tags",        "weight": 10},
    {"label": "has note",        "weight": 10},
    {"label": "is favorited",    "weight": 5},
    {"label": "has owner",       "weight": 15},
    {"label": "has priority",    "weight": 10},
    {"label": "has retry",       "weight": 10},
    {"label": "has timeout",     "weight": 10},
    {"label": "has healthcheck", "weight": 15},
    {"label": "has alert",       "weight": 10},
    {"label": "has notify",      "weight": 5},
    {"label": "has metadata",    "weight": 10},
    {"label": "is locked",       "weight": 5},
]

_TOTAL_WEIGHT = sum(c["weight"] for c in MATURITY_CHECKS)


def _grade(score: int) -> str:
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"


def score_maturity(expression: str, storage_dir: str = ".") -> Dict:
    """Return a maturity report dict for the given cron expression."""
    kwargs = {"storage_dir": storage_dir}

    checks = {
        "has tags":        bool(tags.get_tags(expression, **kwargs)),
        "has note":        notes.get_note(expression, **kwargs) is not None,
        "is favorited":    favorites.get_favorite(expression, **kwargs) is not None,
        "has owner":       ownership.get_owner(expression, **kwargs) is not None,
        "has priority":    priority.get_priority(expression, **kwargs) is not None,
        "has retry":       retry.get_retry(expression, **kwargs) is not None,
        "has timeout":     timeout.get_timeout(expression, **kwargs) is not None,
        "has healthcheck": healthcheck.get_healthcheck(expression, **kwargs) is not None,
        "has alert":       alert.get_alert(expression, **kwargs) is not None,
        "has notify":      notify.get_notify(expression, **kwargs) is not None,
        "has metadata":    bool(metadata.get_all_metadata(expression, **kwargs)),
        "is locked":       lock.get_lock(expression, **kwargs) is not None,
    }

    earned = sum(
        c["weight"] for c in MATURITY_CHECKS if checks.get(c["label"], False)
    )
    score = round((earned / _TOTAL_WEIGHT) * 100)
    missing = [c["label"] for c in MATURITY_CHECKS if not checks.get(c["label"], False)]

    return {
        "expression": expression,
        "score": score,
        "grade": _grade(score),
        "checks": checks,
        "missing": missing,
    }


def format_maturity(report: Dict) -> str:
    """Return a human-readable maturity report string."""
    lines = [
        f"Maturity report for: {report['expression']}",
        f"  Score : {report['score']}/100  (Grade {report['grade']})",
        "  Checks:",
    ]
    for label, passed in report["checks"].items():
        mark = "✓" if passed else "✗"
        lines.append(f"    [{mark}] {label}")
    if report["missing"]:
        lines.append("  Missing: " + ", ".join(report["missing"]))
    return "\n".join(lines)
