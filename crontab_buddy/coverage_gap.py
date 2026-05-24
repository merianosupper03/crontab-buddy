"""Detect gaps in hour coverage across a set of cron expressions."""

from typing import List, Dict, Any
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_parse(expr: str):
    try:
        return CronExpression(expr)
    except CronParseError:
        return None


def _covered_hours(expr: str) -> set:
    """Return the set of hours (0-23) that a cron expression fires in."""
    parsed = _safe_parse(expr)
    if parsed is None:
        return set()
    hour_field = parsed.fields[1]
    if hour_field == "*":
        return set(range(24))
    hours = set()
    for part in hour_field.split(","):
        if "-" in part:
            lo, hi = part.split("-", 1)
            hours.update(range(int(lo), int(hi) + 1))
        elif "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            hours.update(range(start, 24, int(step)))
        else:
            hours.add(int(part))
    return hours


def find_coverage_gaps(expressions: List[str]) -> Dict[str, Any]:
    """Return uncovered hours given a list of cron expressions."""
    covered: set = set()
    valid_count = 0
    invalid = []

    for expr in expressions:
        parsed = _safe_parse(expr)
        if parsed is None:
            invalid.append(expr)
            continue
        valid_count += 1
        covered |= _covered_hours(expr)

    all_hours = set(range(24))
    gaps = sorted(all_hours - covered)

    return {
        "expressions": expressions,
        "valid_count": valid_count,
        "invalid": invalid,
        "covered_hours": sorted(covered),
        "gap_hours": gaps,
        "gap_count": len(gaps),
        "fully_covered": len(gaps) == 0,
    }


def format_coverage_gap(result: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"Expressions checked : {len(result['expressions'])}")
    lines.append(f"Valid               : {result['valid_count']}")
    if result["invalid"]:
        lines.append(f"Invalid             : {', '.join(result['invalid'])}")
    lines.append(f"Covered hours       : {len(result['covered_hours'])}/24")
    if result["fully_covered"]:
        lines.append("Coverage            : FULL (no gaps)")
    else:
        gap_str = ", ".join(str(h) for h in result["gap_hours"])
        lines.append(f"Gap hours           : {gap_str}")
        lines.append(f"Gap count           : {result['gap_count']}")
    return "\n".join(lines)
