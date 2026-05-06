"""CLI commands for the velocity feature."""

from __future__ import annotations

import json

from crontab_buddy.velocity import batch_velocity, compute_velocity


def cmd_velocity_check(args) -> None:
    """Print velocity info for a single expression."""
    try:
        result = compute_velocity(args.expression, getattr(args, "window", "24h"))
        print(result)
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_velocity_level(args) -> None:
    """Print only the velocity level."""
    try:
        result = compute_velocity(args.expression, getattr(args, "window", "24h"))
        print(result.level)
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_velocity_rate(args) -> None:
    """Print only the rate per hour."""
    try:
        result = compute_velocity(args.expression, getattr(args, "window", "24h"))
        print(f"{result.rate_per_hour:.4f}")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_velocity_batch(args) -> None:
    """Print velocity info for multiple expressions."""
    expressions = [e.strip() for e in args.expressions if e.strip()]
    window = getattr(args, "window", "24h")
    try:
        results = batch_velocity(expressions, window)
        for r in results:
            print(r)
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_velocity_json(args) -> None:
    """Print velocity result as JSON."""
    try:
        result = compute_velocity(args.expression, getattr(args, "window", "24h"))
        print(json.dumps({
            "expression": result.expression,
            "window": result.window,
            "count": result.count,
            "rate_per_hour": result.rate_per_hour,
            "level": result.level,
        }, indent=2))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
