"""CLI commands for alert management."""
from __future__ import annotations
from crontab_buddy.alert import (
    set_alert,
    get_alert,
    delete_alert,
    list_alerts,
    VALID_CHANNELS,
    VALID_EVENTS,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_alert_set(args, path: str | None = None) -> None:
    kwargs = {"path": path} if path else {}
    try:
        set_alert(args.expression, args.channel, args.event, getattr(args, "target", None), **kwargs)
        print(f"Alert set: {args.channel} on '{args.event}' for [{args.expression}]")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_alert_get(args, path: str | None = None) -> None:
    kwargs = {"path": path} if path else {}
    alert = get_alert(args.expression, **kwargs)
    if alert is None:
        print(f"No alert configured for [{args.expression}]")
        return
    desc = _describe(args.expression)
    print(f"Expression : {args.expression}")
    print(f"Description: {desc}")
    print(f"Channel    : {alert['channel']}")
    print(f"Event      : {alert['event']}")
    if alert.get("target"):
        print(f"Target     : {alert['target']}")


def cmd_alert_delete(args, path: str | None = None) -> None:
    kwargs = {"path": path} if path else {}
    if delete_alert(args.expression, **kwargs):
        print(f"Alert removed for [{args.expression}]")
    else:
        print(f"No alert found for [{args.expression}]")


def cmd_alert_list(args, path: str | None = None) -> None:
    kwargs = {"path": path} if path else {}
    alerts = list_alerts(**kwargs)
    if not alerts:
        print("No alerts configured.")
        return
    for expr, cfg in alerts.items():
        desc = _describe(expr)
        target_str = f" -> {cfg['target']}" if cfg.get("target") else ""
        print(f"[{expr}] {cfg['channel']} on {cfg['event']}{target_str}  # {desc}")
