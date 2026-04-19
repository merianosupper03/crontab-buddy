"""CLI commands for label management."""
from crontab_buddy import label as lbl
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_label_add(args, path=None):
    kwargs = {"path": path} if path else {}
    ok = lbl.add_label(args.expression, args.label, **kwargs)
    if ok:
        print(f"Labeled '{args.expression}' with '{args.label}'.")
    else:
        print(f"'{args.expression}' already has label '{args.label}'.")


def cmd_label_remove(args, path=None):
    kwargs = {"path": path} if path else {}
    ok = lbl.remove_label(args.expression, args.label, **kwargs)
    if ok:
        print(f"Removed label '{args.label}' from '{args.expression}'.")
    else:
        print(f"Label '{args.label}' not found on '{args.expression}'.")


def cmd_label_list(args, path=None):
    kwargs = {"path": path} if path else {}
    labels = lbl.get_labels(args.expression, **kwargs)
    if labels:
        print(f"Labels for '{args.expression}': {', '.join(labels)}")
    else:
        print(f"No labels for '{args.expression}'.")


def cmd_label_find(args, path=None):
    kwargs = {"path": path} if path else {}
    expressions = lbl.find_by_label(args.label, **kwargs)
    if expressions:
        for expr in expressions:
            print(f"  {expr}  # {_describe(expr)}")
    else:
        print(f"No expressions found with label '{args.label}'.")


def cmd_label_all(args, path=None):
    kwargs = {"path": path} if path else {}
    data = lbl.list_all_labels(**kwargs)
    if not data:
        print("No labels stored.")
        return
    for expr, labels in data.items():
        print(f"  {expr}: {', '.join(labels)}")
