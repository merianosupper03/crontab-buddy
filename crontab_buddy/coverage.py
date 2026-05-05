"""Track which time slots are covered by a set of cron expressions."""

from typing import List, Dict, Any
from crontab_buddy.parser import CronExpression, CronParseError


HOURS = list(range(24))
DAYS_OF_WEEK = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]


def _safe_parse(expr: str):
    try:
        return CronExpression(expr)
    except (CronParseError, ValueError):
        return None


def _hours_covered(expr: CronExpression) -> List[int]:
    """Return list of hours matched by the expression."""
    field = expr.hour
    if field == "*":
        return list(HOURS)
    covered = []
    for h in HOURS:
        if _matches(field, h, 0, 23):
            covered.append(h)
    return covered


def _matches(field: str, value: int, lo: int, hi: int) -> bool:
    for part in field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = lo if base == "*" else int(base.split("-")[0])
            end = hi if base == "*" or "-" not in base else int(base.split("-")[1])
            if start <= value <= end and (value - start) % step == 0:
                return True
        elif "-" in part:
            a, b = part.split("-", 1)
            if int(a) <= value <= int(b):
                return True
        elif part == "*":
            return True
        elif int(part) == value:
            return True
    return False


def compute_coverage(expressions: List[str]) -> Dict[str, Any]:
    """Compute hourly coverage across a list of cron expressions."""
    hour_counts: Dict[int, int] = {h: 0 for h in HOURS}
    valid = 0
    invalid = 0

    for raw in expressions:
        parsed = _safe_parse(raw)
        if parsed is None:
            invalid += 1
            continue
        valid += 1
        for h in _hours_covered(parsed):
            hour_counts[h] += 1

    covered_hours = [h for h, c in hour_counts.items() if c > 0]
    uncovered_hours = [h for h, c in hour_counts.items() if c == 0]
    coverage_pct = round(len(covered_hours) / 24 * 100, 1)

    return {
        "valid": valid,
        "invalid": invalid,
        "covered_hours": covered_hours,
        "uncovered_hours": uncovered_hours,
        "coverage_percent": coverage_pct,
        "hour_counts": hour_counts,
    }


def format_coverage(result: Dict[str, Any]) -> str:
    lines = [
        f"Coverage: {result['coverage_percent']}% ({len(result['covered_hours'])}/24 hours)",
        f"Valid expressions: {result['valid']}, Invalid: {result['invalid']}",
    ]
    if result["uncovered_hours"]:
        unc = ", ".join(str(h) for h in result["uncovered_hours"])
        lines.append(f"Uncovered hours: {unc}")
    else:
        lines.append("All 24 hours are covered.")
    return "\n".join(lines)
