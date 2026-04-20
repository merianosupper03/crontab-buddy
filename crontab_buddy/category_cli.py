"""CLI commands for category management."""
from crontab_buddy.category import (
    add_to_category,
    remove_from_category,
    get_category,
    list_categories,
    delete_category,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_category_add(args) -> None:
    added = add_to_category(args.category, args.expression)
    if added:
        print(f"Added '{args.expression}' to category '{args.category}'.")
    else:
        print(f"'{args.expression}' is already in category '{args.category}'.")


def cmd_category_remove(args) -> None:
    removed = remove_from_category(args.category, args.expression)
    if removed:
        print(f"Removed '{args.expression}' from category '{args.category}'.")
    else:
        print(f"'{args.expression}' not found in category '{args.category}'.")


def cmd_category_list(args) -> None:
    if hasattr(args, "category") and args.category:
        expressions = get_category(args.category)
        if not expressions:
            print(f"Category '{args.category}' is empty or does not exist.")
            return
        print(f"Category: {args.category}")
        for expr in expressions:
            print(f"  {expr}  — {_describe(expr)}")
    else:
        cats = list_categories()
        if not cats:
            print("No categories found.")
            return
        for cat in cats:
            exprs = get_category(cat)
            print(f"{cat} ({len(exprs)} expression(s))")


def cmd_category_delete(args) -> None:
    deleted = delete_category(args.category)
    if deleted:
        print(f"Deleted category '{args.category}'.")
    else:
        print(f"Category '{args.category}' not found.")
