"""CLI commands for execution tracing."""

from __future__ import annotations

from crontab_buddy import tracing
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_trace_start(args, path: str = tracing._DEFAULT_PATH) -> None:
    """Start a new trace span."""
    label = getattr(args, "label", None)
    trace_id = tracing.start_trace(args.expression, label=label, path=path)
    print(f"Trace started: {trace_id}  [{args.expression}]")
    if label:
        print(f"  label: {label}")


def cmd_trace_finish(args, path: str = tracing._DEFAULT_PATH) -> None:
    """Finish an existing trace span."""
    status = getattr(args, "status", "ok") or "ok"
    try:
        found = tracing.finish_trace(
            args.expression, args.trace_id, status=status, path=path
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    if found:
        print(f"Trace {args.trace_id} finished with status '{status}'.")
    else:
        print(f"No running trace '{args.trace_id}' found for expression.")


def cmd_trace_list(args, path: str = tracing._DEFAULT_PATH) -> None:
    """List all trace spans for an expression."""
    spans = tracing.get_traces(args.expression, path=path)
    if not spans:
        print(f"No traces for: {args.expression}")
        return
    print(f"Traces for: {args.expression}  — {_describe(args.expression)}")
    for s in spans:
        dur = f"{s['duration_ms']} ms" if s["duration_ms"] is not None else "running"
        label = f"  [{s['label']}]" if s["label"] else ""
        print(f"  {s['trace_id']}  status={s['status']}  duration={dur}{label}")


def cmd_trace_clear(args, path: str = tracing._DEFAULT_PATH) -> None:
    """Clear all traces for an expression."""
    tracing.clear_traces(args.expression, path=path)
    print(f"Traces cleared for: {args.expression}")


def cmd_trace_list_all(args, path: str = tracing._DEFAULT_PATH) -> None:
    """List every expression that has trace data."""
    exprs = tracing.list_traced_expressions(path=path)
    if not exprs:
        print("No traced expressions found.")
        return
    print(f"{len(exprs)} traced expression(s):")
    for expr in exprs:
        print(f"  {expr}  — {_describe(expr)}")
