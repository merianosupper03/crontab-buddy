"""CLI commands for wavelength assessment."""
from __future__ import annotations
import json
from crontab_buddy.wavelength import assess_wavelength, batch_wavelength


def cmd_wavelength_check(args) -> None:
    result = assess_wavelength(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Period (s) : {result.period_seconds:.1f}")
    print(f"Score      : {result.score}")
    print(f"Label      : {result.label}")


def cmd_wavelength_score(args) -> None:
    result = assess_wavelength(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.score)


def cmd_wavelength_label(args) -> None:
    result = assess_wavelength(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.label)


def cmd_wavelength_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_wavelength(expressions)
    for r in results:
        if r.error:
            print(f"  {r.expression!r:30s}  ERROR: {r.error}")
        else:
            print(f"  {r.expression!r:30s}  {r.period_seconds:10.1f}s  {r.label}")


def cmd_wavelength_json(args) -> None:
    result = assess_wavelength(args.expression)
    data = {
        "expression": result.expression,
        "period_seconds": result.period_seconds,
        "score": result.score,
        "label": result.label,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
