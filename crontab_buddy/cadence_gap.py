"""Detect gaps in cadence coverage across a set of cron expressions."""
from typing import List, Dict, Any
from crontab_buddy.parser import CronExpression, CronParseError


HOURS = list(range(24))


def _safe_parse(expr: str):
    try:
        return CronExpression(expr)
    except CronParseError:
        return None


def _covered_hours(expr: str) -> set:
    parsed = _safe_parse(expr)
    if parsed is None:
        return set()
    hour_field = parsed.fields[1]
    covered = set()
    if hour_field == "*":
        return set(HOURS)
    for part in hour_field.split(","):
        if "-" in part:
            a, b = part.split("-", 1)
            covered.update(range(int(a), int(b) + 1))
        elif "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            covered.update(range(start, 24, int(step)))
        else:
            covered.add(int(part))
    return covered


def find_cadence_gaps(expressions: List[str]) -> Dict[str, Any]:
    """Return hours not covered by any of the given expressions."""
    covered = set()
    for expr in expressions:
        covered |= _covered_hours(expr)
    gaps = sorted(set(HOURS) - covered)
    coverage_pct = round(len(covered) / 24 * 100, 1)
    return {
        "covered_hours": sorted(covered),
        "gap_hours": gaps,
        "coverage_percent": coverage_pct,
        "has_gaps": len(gaps) > 0,
    }


def format_cadence_gap(result: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"Coverage: {result['coverage_percent']}%")
    if result["has_gaps"]:
        gap_str = ", ".join(str(h) for h in result["gap_hours"])
        lines.append(f"Gap hours (UTC): {gap_str}")
    else:
        lines.append("No gaps — all 24 hours covered.")
    return "\n".join(lines)
