"""CLI commands for drift detection."""

from datetime import datetime
from crontab_buddy.drift import detect_drift, drift_summary


def _parse_dt(value: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse datetime: {value!r}")


def cmd_drift_check(args, print_fn=print) -> None:
    """Check drift for a single expression against an actual run time."""
    try:
        actual = _parse_dt(args.actual)
        reference = _parse_dt(args.reference) if getattr(args, "reference", None) else None
        result = detect_drift(args.expression, actual, reference)
        print_fn(str(result))
        print_fn(f"  delta_seconds : {result.delta_seconds:.0f}")
        print_fn(f"  drifted       : {result.drifted}")
    except ValueError as exc:
        print_fn(f"Error: {exc}")


def cmd_drift_batch(args, print_fn=print) -> None:
    """Check drift for multiple expression:actual pairs (comma-separated)."""
    pairs = getattr(args, "pairs", "") or ""
    results = []
    for pair in pairs.split(","):
        pair = pair.strip()
        if ":" not in pair:
            print_fn(f"Skipping invalid pair: {pair!r}")
            continue
        expr, actual_str = pair.split(":", 1)
        try:
            actual = _parse_dt(actual_str.strip())
            result = detect_drift(expr.strip(), actual)
            results.append(result)
            print_fn(str(result))
        except ValueError as exc:
            print_fn(f"  Error for {expr!r}: {exc}")

    if results:
        summary = drift_summary(results)
        print_fn("")
        print_fn(f"Summary: {summary['drifted']}/{summary['total']} drifted, "
                 f"max={summary['max_drift_seconds']:.0f}s, "
                 f"avg={summary['avg_drift_seconds']:.1f}s")
