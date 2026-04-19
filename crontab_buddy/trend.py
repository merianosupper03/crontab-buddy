"""Trend analysis: detect which expressions are gaining or losing usage over time."""

from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any

from crontab_buddy.history import get_history
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except (CronParseError, Exception):
        return expr


def _bucket(ts: str, days: int) -> str:
    """Return 'recent' or 'older' depending on whether ts falls within last `days`."""
    try:
        dt = datetime.fromisoformat(ts)
    except Exception:
        return "older"
    cutoff = datetime.now() - timedelta(days=days)
    return "recent" if dt >= cutoff else "older"


def compute_trend(days: int = 7, history_path: str | None = None) -> List[Dict[str, Any]]:
    """Compare expression usage in the last `days` vs before that.

    Returns a list of dicts sorted by trend score descending.
    """
    kwargs = {"path": history_path} if history_path else {}
    entries = get_history(**kwargs)

    recent: Dict[str, int] = defaultdict(int)
    older: Dict[str, int] = defaultdict(int)

    for entry in entries:
        expr = entry.get("expression", "")
        ts = entry.get("timestamp", "")
        bucket = _bucket(ts, days)
        if bucket == "recent":
            recent[expr] += 1
        else:
            older[expr] += 1

    all_exprs = set(recent) | set(older)
    results = []
    for expr in all_exprs:
        r = recent.get(expr, 0)
        o = older.get(expr, 0)
        score = r - o
        results.append({
            "expression": expr,
            "description": _safe_humanize(expr),
            "recent_count": r,
            "older_count": o,
            "trend_score": score,
            "trend": "rising" if score > 0 else ("falling" if score < 0 else "stable"),
        })

    results.sort(key=lambda x: x["trend_score"], reverse=True)
    return results


def format_trend(results: List[Dict[str, Any]]) -> str:
    if not results:
        return "No trend data available."
    lines = ["Expression Trends", "=" * 40]
    for r in results:
        arrow = {"rising": "↑", "falling": "↓", "stable": "→"}[r["trend"]]
        lines.append(
            f"{arrow} [{r['trend'].upper():7}] {r['expression']:20} "
            f"recent={r['recent_count']} older={r['older_count']}  — {r['description']}"
        )
    return "\n".join(lines)
