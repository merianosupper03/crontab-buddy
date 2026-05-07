"""CLI commands for dispersion analysis."""

import json

from crontab_buddy.dispersion import assess_dispersion


def cmd_dispersion_check(args) -> None:
    """Print a human-readable dispersion report for an expression."""
    result = assess_dispersion(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Label      : {result.label}")
    print(f"Mean gap   : {result.mean_interval:.1f} min")
    print(f"Std dev    : {result.std_dev:.1f} min")
    print(f"Fire count : {len(result.intervals) + 1} times/day")


def cmd_dispersion_score(args) -> None:
    """Print only the numeric dispersion score."""
    result = assess_dispersion(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_dispersion_label(args) -> None:
    """Print only the dispersion label (uniform/spread/uneven/clustered)."""
    result = assess_dispersion(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.label)


def cmd_dispersion_batch(args) -> None:
    """Check dispersion for multiple space-separated expressions."""
    expressions = args.expressions
    for expr in expressions:
        result = assess_dispersion(expr)
        if result.error:
            print(f"{expr!r:30s}  error: {result.error}")
        else:
            print(f"{expr!r:30s}  {result.label:10s}  score={result.score:.4f}")


def cmd_dispersion_json(args) -> None:
    """Output dispersion result as JSON."""
    result = assess_dispersion(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "label": result.label,
        "mean_interval": result.mean_interval,
        "std_dev": result.std_dev,
        "fire_count": len(result.intervals) + 1 if result.intervals else 0,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
