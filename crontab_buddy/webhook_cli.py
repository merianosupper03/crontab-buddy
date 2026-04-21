"""CLI commands for webhook management."""

from crontab_buddy.webhook import set_webhook, get_webhook, delete_webhook, list_webhooks
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_webhook_set(args, path=None):
    kwargs = {"path": path} if path else {}
    try:
        set_webhook(
            args.expression,
            args.url,
            on_success=not getattr(args, "no_success", False),
            on_failure=not getattr(args, "no_failure", False),
            **kwargs,
        )
        print(f"Webhook set for '{args.expression}' -> {args.url}")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_webhook_get(args, path=None):
    kwargs = {"path": path} if path else {}
    entry = get_webhook(args.expression, **kwargs)
    if entry is None:
        print(f"No webhook registered for '{args.expression}'.")
    else:
        print(f"Expression : {args.expression}")
        print(f"Description: {_describe(args.expression)}")
        print(f"URL        : {entry['url']}")
        print(f"On success : {entry['on_success']}")
        print(f"On failure : {entry['on_failure']}")


def cmd_webhook_delete(args, path=None):
    kwargs = {"path": path} if path else {}
    removed = delete_webhook(args.expression, **kwargs)
    if removed:
        print(f"Webhook removed for '{args.expression}'.")
    else:
        print(f"No webhook found for '{args.expression}'.")


def cmd_webhook_list(args, path=None):
    kwargs = {"path": path} if path else {}
    entries = list_webhooks(**kwargs)
    if not entries:
        print("No webhooks registered.")
        return
    for expr, cfg in entries.items():
        desc = _describe(expr)
        flags = []
        if cfg["on_success"]:
            flags.append("success")
        if cfg["on_failure"]:
            flags.append("failure")
        print(f"  {expr} ({desc}) -> {cfg['url']} [{', '.join(flags)}]")
