"""CLI commands for recency assessment."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from crontab_buddy.recency import assess_recency, batch_recency


def _parse_iso(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO datetime: {value!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def cmd_recency_check(args, print_fn=print) -> None:
    """Print full recency assessment for an expression."""
    last_seen = _parse_iso(args.last_seen) if args.last_seen else None
    result = assess_recency(args.expression, last_seen)
    print_fn(f"Expression : {result.expression}")
    print_fn(f"Label      : {result.label}")
    print_fn(f"Score      : {result.score:.3f}")
    if result.minutes_ago is not None:
        print_fn(f"Minutes ago: {result.minutes_ago}")
    else:
        print_fn("Last seen  : never")


def cmd_recency_score(args, print_fn=print) -> None:
    """Print only the numeric recency score."""
    last_seen = _parse_iso(args.last_seen) if args.last_seen else None
    result = assess_recency(args.expression, last_seen)
    print_fn(f"{result.score:.3f}")


def cmd_recency_label(args, print_fn=print) -> None:
    """Print only the recency label."""
    last_seen = _parse_iso(args.last_seen) if args.last_seen else None
    result = assess_recency(args.expression, last_seen)
    print_fn(result.label)


def cmd_recency_json(args, print_fn=print) -> None:
    """Print recency result as JSON."""
    last_seen = _parse_iso(args.last_seen) if args.last_seen else None
    result = assess_recency(args.expression, last_seen)
    data = {
        "expression": result.expression,
        "label": result.label,
        "score": result.score,
        "minutes_ago": result.minutes_ago,
        "last_seen": result.last_seen.isoformat() if result.last_seen else None,
    }
    print_fn(json.dumps(data, indent=2))


def cmd_recency_batch(args, print_fn=print) -> None:
    """Assess recency for multiple expressions (no last_seen → never)."""
    entries = [(expr.strip(), None) for expr in args.expressions]
    results = batch_recency(entries)
    for r in results:
        print_fn(f"{r.expression:<25} {r.label:<12} score={r.score:.3f}")
