"""Heatmap: visualize cron expression activity across hours and days."""

from typing import Dict, List, Optional
from crontab_buddy.parser import CronExpression, CronParseError


DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
HOURS = list(range(24))


def _safe_parse(expression: str) -> Optional[CronExpression]:
    try:
        return CronExpression(expression)
    except CronParseError:
        return None


def _matches(field: str, value: int) -> bool:
    if field == "*":
        return True
    if "/" in field:
        parts = field.split("/")
        step = int(parts[1])
        return value % step == 0
    if "-" in field:
        lo, hi = field.split("-")
        return int(lo) <= value <= int(hi)
    if "," in field:
        return value in [int(v) for v in field.split(",")]
    return value == int(field)


def build_heatmap(expressions: List[str]) -> Dict[str, Dict[int, int]]:
    """Return a heatmap dict: day_name -> hour -> hit_count."""
    heatmap: Dict[str, Dict[int, int]] = {
        day: {h: 0 for h in HOURS} for day in DAYS
    }
    for expr_str in expressions:
        expr = _safe_parse(expr_str)
        if expr is None:
            continue
        for dow_val, day_name in enumerate(DAYS):
            if not _matches(expr.day_of_week, dow_val):
                continue
            for hour in HOURS:
                if _matches(expr.hour, hour):
                    heatmap[day_name][hour] += 1
    return heatmap


def format_heatmap(heatmap: Dict[str, Dict[int, int]]) -> str:
    """Render the heatmap as a simple ASCII grid."""
    header = "     " + "".join(f"{h:3}" for h in HOURS)
    lines = [header]
    for day in DAYS:
        row = f"{day:<5}"
        for h in HOURS:
            count = heatmap[day][h]
            if count == 0:
                cell = "  ."
            elif count < 3:
                cell = f"  {count}"
            else:
                cell = f" {count:2}"
            row += cell
        lines.append(row)
    return "\n".join(lines)


def summary_heatmap(heatmap: Dict[str, Dict[int, int]]) -> Dict[str, int]:
    """Return total hits per day."""
    return {day: sum(heatmap[day].values()) for day in DAYS}
