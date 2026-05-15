"""CLI commands for density analysis."""

from .density import compute_density, format_density


def cmd_density_check(args) -> None:
    expressions = args.expressions if hasattr(args, "expressions") else [args.expression]
    window = getattr(args, "window", "24h")
    result = compute_density(expressions, window=window)
    print(f"Expressions : {', '.join(expressions)}")
    print(f"Window      : {window}")
    print(f"Fires       : {result.windows.get(window, 0)}")
    print(f"Label       : {result.label}")


def cmd_density_label(args) -> None:
    expressions = args.expressions if hasattr(args, "expressions") else [args.expression]
    window = getattr(args, "window", "24h")
    result = compute_density(expressions, window=window)
    print(result.label)


def cmd_density_fires(args) -> None:
    expressions = args.expressions if hasattr(args, "expressions") else [args.expression]
    window = getattr(args, "window", "24h")
    result = compute_density(expressions, window=window)
    print(result.windows.get(window, 0))


def cmd_density_batch(args) -> None:
    expressions = args.expressions
    window = getattr(args, "window", "24h")
    for expr in expressions:
        try:
            result = compute_density([expr], window=window)
            fires = result.windows.get(window, 0)
            print(f"{expr:30s}  {fires:6d} fires  [{result.label}]")
        except Exception as exc:
            print(f"{expr:30s}  ERROR: {exc}")


def cmd_density_json(args) -> None:
    import json
    expressions = args.expressions if hasattr(args, "expressions") else [args.expression]
    window = getattr(args, "window", "24h")
    result = compute_density(expressions, window=window)
    print(json.dumps({
        "expressions": expressions,
        "window": window,
        "fires": result.windows.get(window, 0),
        "label": result.label,
        "windows": result.windows,
    }, indent=2))
