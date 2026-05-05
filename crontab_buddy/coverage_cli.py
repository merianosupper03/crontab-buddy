"""CLI commands for coverage analysis."""

import json
from crontab_buddy.coverage import compute_coverage, format_coverage


def cmd_coverage_check(args, print_fn=print):
    """Check hourly coverage for a list of expressions."""
    expressions = args.expressions
    result = compute_coverage(expressions)
    print_fn(format_coverage(result))


def cmd_coverage_json(args, print_fn=print):
    """Output coverage result as JSON."""
    expressions = args.expressions
    result = compute_coverage(expressions)
    # hour_counts keys are ints; convert for JSON
    result["hour_counts"] = {str(k): v for k, v in result["hour_counts"].items()}
    print_fn(json.dumps(result, indent=2))


def cmd_coverage_gaps(args, print_fn=print):
    """Print only uncovered hours."""
    expressions = args.expressions
    result = compute_coverage(expressions)
    if not result["uncovered_hours"]:
        print_fn("No gaps — all 24 hours are covered.")
    else:
        gaps = ", ".join(str(h) for h in result["uncovered_hours"])
        print_fn(f"Uncovered hours: {gaps}")
