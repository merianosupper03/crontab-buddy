"""CLI commands for anomaly detection."""

import json
from crontab_buddy.anomaly import detect_anomalies


def cmd_anomaly_check(args, print_fn=print) -> None:
    """Check a single expression for anomalies and print results."""
    result = detect_anomalies(args.expression)
    if result.ok:
        print_fn(f"OK: {args.expression} — no anomalies detected")
    else:
        print_fn(f"ANOMALIES detected in: {args.expression}")
        for idx, reason in enumerate(result.anomalies, 1):
            print_fn(f"  {idx}. {reason}")


def cmd_anomaly_batch(args, print_fn=print) -> None:
    """Check multiple expressions (newline-separated) for anomalies."""
    expressions = [e.strip() for e in args.expressions.splitlines() if e.strip()]
    total = len(expressions)
    flagged = 0
    for expr in expressions:
        result = detect_anomalies(expr)
        status = "OK" if result.ok else "ANOMALY"
        print_fn(f"[{status}] {expr}")
        if not result.ok:
            flagged += 1
            for reason in result.anomalies:
                print_fn(f"       - {reason}")
    print_fn(f"\n{flagged}/{total} expression(s) flagged.")


def cmd_anomaly_json(args, print_fn=print) -> None:
    """Output anomaly check result as JSON."""
    result = detect_anomalies(args.expression)
    payload = {
        "expression": result.expression,
        "ok": result.ok,
        "anomalies": result.anomalies,
    }
    print_fn(json.dumps(payload, indent=2))
