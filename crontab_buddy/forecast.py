"""Forecast module: predict upcoming run counts over a time window."""

from datetime import datetime, timedelta
from typing import Dict, List

from crontab_buddy.scheduler import next_runs
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


WINDOW_OPTIONS = {
    "hour": 1,
    "day": 24,
    "week": 24 * 7,
    "month": 24 * 30,
}


def _safe_parse(expression: str):
    try:
        return CronExpression(expression)
    except CronParseError:
        return None


def forecast(
    expression: str,
    window_hours: int = 24,
    from_dt: datetime = None,
) -> Dict:
    """Return forecast data for an expression over a given window in hours."""
    if from_dt is None:
        from_dt = datetime.utcnow()

    expr = _safe_parse(expression)
    if expr is None:
        return {
            "expression": expression,
            "valid": False,
            "window_hours": window_hours,
            "run_count": 0,
            "runs": [],
            "description": None,
        }

    until = from_dt + timedelta(hours=window_hours)
    # Fetch enough runs to cover the window
    candidates = next_runs(expression, count=window_hours * 60, from_dt=from_dt)
    runs_in_window: List[datetime] = [r for r in candidates if r < until]

    return {
        "expression": expression,
        "valid": True,
        "window_hours": window_hours,
        "run_count": len(runs_in_window),
        "runs": runs_in_window,
        "description": humanize(expr),
    }


def format_forecast(data: Dict) -> str:
    """Return a human-readable forecast summary."""
    if not data["valid"]:
        return f"Invalid expression: {data['expression']}"

    lines = [
        f"Expression : {data['expression']}",
        f"Description: {data['description']}",
        f"Window     : {data['window_hours']} hour(s)",
        f"Run count  : {data['run_count']}",
    ]
    if data["runs"]:
        lines.append("Next runs  :")
        for r in data["runs"][:5]:
            lines.append(f"  - {r.strftime('%Y-%m-%d %H:%M')} UTC")
        if data["run_count"] > 5:
            lines.append(f"  ... and {data['run_count'] - 5} more")
    return "\n".join(lines)
