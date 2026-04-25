"""CLI commands for managing health checks on cron expressions."""
from __future__ import annotations

from typing import Any

from crontab_buddy.healthcheck import (
    VALID_METHODS,
    delete_healthcheck,
    get_healthcheck,
    list_healthchecks,
    set_healthcheck,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_healthcheck_set(args: Any, path: str | None = None) -> None:
    kwargs: dict = {"expression": args.expression, "url": args.url}
    if hasattr(args, "method") and args.method:
        kwargs["method"] = args.method
    if hasattr(args, "grace") and args.grace is not None:
        kwargs["grace_seconds"] = args.grace
    if path:
        kwargs["path"] = path
    try:
        set_healthcheck(**kwargs)
        print(f"Health check set for: {args.expression}")
        print(f"  URL: {args.url}")
        print(f"  Schedule: {_describe(args.expression)}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_healthcheck_get(args: Any, path: str | None = None) -> None:
    kw = {"expression": args.expression}
    if path:
        kw["path"] = path
    hc = get_healthcheck(**kw)
    if hc is None:
        print(f"No health check found for: {args.expression}")
        return
    print(f"Expression : {args.expression}")
    print(f"Description: {_describe(args.expression)}")
    print(f"URL        : {hc['url']}")
    print(f"Method     : {hc['method']}")
    print(f"Grace      : {hc['grace_seconds']}s")


def cmd_healthcheck_delete(args: Any, path: str | None = None) -> None:
    kw = {"expression": args.expression}
    if path:
        kw["path"] = path
    removed = delete_healthcheck(**kw)
    if removed:
        print(f"Removed health check for: {args.expression}")
    else:
        print(f"No health check found for: {args.expression}")


def cmd_healthcheck_list(args: Any, path: str | None = None) -> None:
    kw = {}
    if path:
        kw["path"] = path
    items = list_healthchecks(**kw)
    if not items:
        print("No health checks configured.")
        return
    for item in items:
        desc = _describe(item["expression"])
        print(f"{item['expression']} | {desc} | {item['url']} [{item['method']}] grace={item['grace_seconds']}s")
