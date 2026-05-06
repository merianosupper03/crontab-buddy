"""CLI commands for throughput analysis."""

from crontab_buddy.throughput import estimate_runs, throughput_report, format_throughput, WINDOWS
import json


def cmd_throughput_estimate(args) -> None:
    """Estimate runs for a single expression in a given window."""
    window = getattr(args, "window", "24h")
    if window not in WINDOWS:
        print(f"Unknown window '{window}'. Valid options: {', '.join(WINDOWS)}")
        return
    result = estimate_runs(args.expression, WINDOWS[window])
    if result is None:
        print(f"Invalid expression: {args.expression!r}")
        return
    print(f"Expression : {args.expression}")
    print(f"Window     : {window}")
    print(f"Est. runs  : ~{result}")


def cmd_throughput_batch(args) -> None:
    """Show throughput for multiple space-separated expressions."""
    window = getattr(args, "window", "24h")
    if window not in WINDOWS:
        print(f"Unknown window '{window}'. Valid options: {', '.join(WINDOWS)}")
        return
    expressions = args.expressions
    if not expressions:
        print("No expressions provided.")
        return
    report = throughput_report(expressions, window)
    print(f"Throughput report [{window}]:")
    print(format_throughput(report))


def cmd_throughput_json(args) -> None:
    """Output throughput report as JSON."""
    window = getattr(args, "window", "24h")
    if window not in WINDOWS:
        print(json.dumps({"error": f"Unknown window '{window}'"}))
        return
    expressions = args.expressions
    report = throughput_report(expressions, window)
    print(json.dumps(report, indent=2))
