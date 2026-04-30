"""CLI helpers for the impact assessment feature."""

from __future__ import annotations

from crontab_buddy.impact import assess_impact
from crontab_buddy.parser import CronParseError


def cmd_impact_assess(args) -> None:
    """Print an impact assessment for a cron expression."""
    expression = args.expression
    try:
        result = assess_impact(expression)
        print(str(result))
    except CronParseError as exc:
        print(f"Error: {exc}")


def cmd_impact_level(args) -> None:
    """Print only the impact level (low/moderate/elevated/high)."""
    expression = args.expression
    try:
        result = assess_impact(expression)
        print(result.level)
    except CronParseError as exc:
        print(f"Error: {exc}")


def cmd_impact_json(args) -> None:
    """Print the impact assessment as a JSON object."""
    import json

    expression = args.expression
    try:
        result = assess_impact(expression)
        data = {
            "expression": result.expression,
            "level": result.level,
            "runs_per_day": result.runs_per_day,
            "runs_per_week": result.runs_per_week,
            "runs_per_month": result.runs_per_month,
            "interval_seconds": result.interval_seconds,
        }
        print(json.dumps(data, indent=2))
    except CronParseError as exc:
        print(json.dumps({"error": str(exc)}))
