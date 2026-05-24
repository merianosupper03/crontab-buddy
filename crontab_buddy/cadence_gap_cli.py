"""CLI commands for cadence gap detection."""
import json
from crontab_buddy.cadence_gap import find_cadence_gaps, format_cadence_gap


def cmd_cadence_gap_check(args) -> None:
    """Print a human-readable cadence gap report."""
    expressions = args.expressions
    result = find_cadence_gaps(expressions)
    print(format_cadence_gap(result))


def cmd_cadence_gap_hours(args) -> None:
    """Print only the gap hours as a space-separated list."""
    result = find_cadence_gaps(args.expressions)
    if result["gap_hours"]:
        print(" ".join(str(h) for h in result["gap_hours"]))
    else:
        print("none")


def cmd_cadence_gap_percent(args) -> None:
    """Print coverage percentage."""
    result = find_cadence_gaps(args.expressions)
    print(result["coverage_percent"])


def cmd_cadence_gap_json(args) -> None:
    """Print gap result as JSON."""
    result = find_cadence_gaps(args.expressions)
    print(json.dumps(result, indent=2))
