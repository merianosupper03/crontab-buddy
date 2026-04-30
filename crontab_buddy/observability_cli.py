"""CLI commands for managing observability settings."""

from crontab_buddy.observability import (
    delete_observability,
    get_observability,
    list_observability,
    set_observability,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_observability_set(args) -> None:
    try:
        set_observability(
            args.expression,
            log_level=getattr(args, "log_level", "info"),
            trace_backend=getattr(args, "trace_backend", "none"),
            metrics_enabled=getattr(args, "metrics_enabled", False),
            path=args.path,
        )
        print(f"Observability saved for: {args.expression}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_observability_get(args) -> None:
    config = get_observability(args.expression, path=args.path)
    if config is None:
        print(f"No observability config for: {args.expression}")
        return
    print(f"Expression : {args.expression}")
    print(f"Description: {_describe(args.expression)}")
    print(f"Log level  : {config['log_level']}")
    print(f"Trace      : {config['trace_backend']}")
    print(f"Metrics    : {'enabled' if config['metrics_enabled'] else 'disabled'}")


def cmd_observability_delete(args) -> None:
    removed = delete_observability(args.expression, path=args.path)
    if removed:
        print(f"Removed observability config for: {args.expression}")
    else:
        print(f"No config found for: {args.expression}")


def cmd_observability_list(args) -> None:
    configs = list_observability(path=args.path)
    if not configs:
        print("No observability configs stored.")
        return
    for expr, cfg in configs.items():
        metrics = "metrics=on" if cfg["metrics_enabled"] else "metrics=off"
        print(
            f"{expr}  [{cfg['log_level']} | trace:{cfg['trace_backend']} | {metrics}]"
            f"  # {_describe(expr)}"
        )
