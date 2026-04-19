"""CLI commands for the report feature."""

from crontab_buddy.report import build_report, format_report


def cmd_report(args) -> None:
    """Print a report for one or more expressions."""
    expressions = args.expressions
    count = getattr(args, "count", 3)
    if not expressions:
        print("No expressions provided.")
        return
    report = build_report(expressions, count=count)
    print(format_report(report))


def cmd_report_json(args) -> None:
    """Print a JSON report for one or more expressions."""
    import json
    expressions = args.expressions
    count = getattr(args, "count", 3)
    if not expressions:
        print(json.dumps([]))
        return
    report = build_report(expressions, count=count)
    print(json.dumps(report, indent=2))
