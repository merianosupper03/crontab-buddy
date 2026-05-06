"""CLI commands for decay scoring."""

from datetime import datetime, timezone

from .decay import compute_decay, is_stale, format_decay


def _parse_iso(dt_str: str) -> datetime:
    """Parse an ISO-8601 datetime string into a UTC-aware datetime."""
    try:
        dt = datetime.fromisoformat(dt_str)
    except ValueError:
        raise ValueError(f"Cannot parse datetime: {dt_str!r}. Use ISO-8601 format.")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def cmd_decay_score(args, print_fn=print):
    """Compute and display the decay score for an expression."""
    try:
        last_used = _parse_iso(args.last_used)
    except ValueError as exc:
        print_fn(f"Error: {exc}")
        return

    half_life = getattr(args, "half_life", "normal")
    try:
        result = compute_decay(args.expression, last_used, half_life=half_life)
    except ValueError as exc:
        print_fn(f"Error: {exc}")
        return

    print_fn(format_decay(result))


def cmd_decay_check(args, print_fn=print):
    """Check whether an expression is considered stale."""
    try:
        last_used = _parse_iso(args.last_used)
    except ValueError as exc:
        print_fn(f"Error: {exc}")
        return

    half_life = getattr(args, "half_life", "normal")
    threshold = float(getattr(args, "threshold", 0.1))

    try:
        result = compute_decay(args.expression, last_used, half_life=half_life)
    except ValueError as exc:
        print_fn(f"Error: {exc}")
        return

    stale = is_stale(result, threshold=threshold)
    status = "STALE" if stale else "FRESH"
    print_fn(f"{args.expression}  score={result.score}  status={status}")


def cmd_decay_json(args, print_fn=print):
    """Output decay result as JSON."""
    import json
    try:
        last_used = _parse_iso(args.last_used)
    except ValueError as exc:
        print_fn(f"Error: {exc}")
        return

    half_life = getattr(args, "half_life", "normal")
    try:
        result = compute_decay(args.expression, last_used, half_life=half_life)
    except ValueError as exc:
        print_fn(f"Error: {exc}")
        return

    print_fn(json.dumps({
        "expression": result.expression,
        "score": result.score,
        "age_days": result.age_days,
        "half_life": result.half_life,
        "stale": is_stale(result),
    }, indent=2))
