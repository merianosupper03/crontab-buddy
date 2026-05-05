"""CLI commands for the forecast feature."""

import json
from datetime import datetime

from crontab_buddy.forecast import forecast, format_forecast, WINDOW_OPTIONS


def cmd_forecast(args) -> None:
    """Print a human-readable forecast for the given expression."""
    window = getattr(args, "window", "day")
    window_hours = WINDOW_OPTIONS.get(window, 24)
    data = forecast(args.expression, window_hours=window_hours)
    print(format_forecast(data))


def cmd_forecast_count(args) -> None:
    """Print only the run count for the expression within the window."""
    window = getattr(args, "window", "day")
    window_hours = WINDOW_OPTIONS.get(window, 24)
    data = forecast(args.expression, window_hours=window_hours)
    if not data["valid"]:
        print(f"Invalid expression: {args.expression}")
        return
    print(data["run_count"])


def cmd_forecast_json(args) -> None:
    """Print forecast data as JSON."""
    window = getattr(args, "window", "day")
    window_hours = WINDOW_OPTIONS.get(window, 24)
    data = forecast(args.expression, window_hours=window_hours)
    out = {
        "expression": data["expression"],
        "valid": data["valid"],
        "window_hours": data["window_hours"],
        "run_count": data["run_count"],
        "description": data["description"],
        "runs": [r.strftime("%Y-%m-%d %H:%M") for r in data["runs"][:10]],
    }
    print(json.dumps(out, indent=2))
