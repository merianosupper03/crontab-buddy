"""CLI helpers for the pulse module."""
from __future__ import annotations
import json
from crontab_buddy.pulse import assess_pulse, batch_pulse


def cmd_pulse_check(args) -> None:
    result = assess_pulse(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Level      : {result.level}")
    print(f"Score      : {result.score:.3f}")
    if result.interval_seconds is not None:
        print(f"Interval   : {result.interval_seconds:.0f}s")


def cmd_pulse_score(args) -> None:
    result = assess_pulse(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_pulse_level(args) -> None:
    result = assess_pulse(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.level)


def cmd_pulse_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_pulse(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  {r.level:10s}  {r.score:.3f}")


def cmd_pulse_json(args) -> None:
    result = assess_pulse(args.expression)
    data = {
        "expression": result.expression,
        "interval_seconds": result.interval_seconds,
        "score": result.score,
        "level": result.level,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
