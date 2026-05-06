"""Throughput analysis: estimate how many runs occur in a given time window."""

from typing import Dict, List, Optional
from crontab_buddy.parser import CronExpression, CronParseError


WINDOWS: Dict[str, int] = {
    "1h": 3600,
    "6h": 21600,
    "12h": 43200,
    "24h": 86400,
    "7d": 604800,
    "30d": 2592000,
}


def _safe_parse(expression: str) -> Optional[CronExpression]:
    try:
        return CronExpression(expression)
    except (CronParseError, ValueError):
        return None


def estimate_runs(expression: str, window_seconds: int) -> Optional[int]:
    """Estimate number of times expression fires within window_seconds."""
    expr = _safe_parse(expression)
    if expr is None:
        return None
    # Determine the period in seconds between fires
    minute, hour, dom, month, dow = (
        expr.minute, expr.hour, expr.dom, expr.month, expr.dow
    )

    def _period(field: str, unit_seconds: int) -> int:
        if field == "*":
            return unit_seconds
        if field.startswith("*/"):
            try:
                step = int(field[2:])
                return unit_seconds * step
            except ValueError:
                pass
        return unit_seconds  # conservative fallback

    minute_period = _period(minute, 60)
    hour_period = _period(hour, 3600)
    dom_period = _period(dom, 86400)
    month_period = _period(month, 2592000)

    base_period = max(minute_period, hour_period, dom_period, month_period)
    if base_period <= 0:
        return 0
    return max(0, window_seconds // base_period)


def throughput_report(expressions: List[str], window: str = "24h") -> List[Dict]:
    """Return throughput info for a list of expressions over a named window."""
    seconds = WINDOWS.get(window, WINDOWS["24h"])
    results = []
    for expr in expressions:
        runs = estimate_runs(expr, seconds)
        results.append({
            "expression": expr,
            "window": window,
            "estimated_runs": runs,
            "valid": runs is not None,
        })
    return results


def format_throughput(report: List[Dict]) -> str:
    """Format throughput report as a human-readable string."""
    lines = []
    for entry in report:
        expr = entry["expression"]
        window = entry["window"]
        if not entry["valid"]:
            lines.append(f"  {expr!r:30s}  [{window}]  INVALID")
        else:
            runs = entry["estimated_runs"]
            lines.append(f"  {expr!r:30s}  [{window}]  ~{runs} run(s)")
    return "\n".join(lines) if lines else "  (no expressions)"
