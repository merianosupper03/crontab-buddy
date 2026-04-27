"""CLI commands for the annotation feature."""

from crontab_buddy.annotation import (
    add_annotation,
    get_annotations,
    delete_annotation,
    clear_annotations,
    list_all_annotations,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_annotation_add(args, print_fn=print) -> None:
    """Add an annotation to an expression."""
    try:
        entry = add_annotation(args.expression, args.text, getattr(args, "author", None))
        author_str = f" [{entry['author']}]" if entry["author"] else ""
        print_fn(f"Annotation added{author_str}: {entry['text']}")
    except ValueError as exc:
        print_fn(f"Error: {exc}")


def cmd_annotation_get(args, print_fn=print) -> None:
    """List all annotations for an expression."""
    entries = get_annotations(args.expression)
    if not entries:
        print_fn(f"No annotations for: {args.expression}")
        return
    print_fn(f"Annotations for {args.expression} — {_describe(args.expression)}")
    for i, entry in enumerate(entries):
        author_str = f" [{entry['author']}]" if entry.get("author") else ""
        print_fn(f"  [{i}]{author_str} {entry['text']}")


def cmd_annotation_delete(args, print_fn=print) -> None:
    """Delete an annotation by index."""
    if delete_annotation(args.expression, args.index):
        print_fn(f"Annotation [{args.index}] deleted from: {args.expression}")
    else:
        print_fn(f"No annotation at index {args.index} for: {args.expression}")


def cmd_annotation_clear(args, print_fn=print) -> None:
    """Clear all annotations for an expression."""
    count = clear_annotations(args.expression)
    print_fn(f"Cleared {count} annotation(s) for: {args.expression}")


def cmd_annotation_list(args, print_fn=print) -> None:
    """List all annotated expressions."""
    all_data = list_all_annotations()
    if not all_data:
        print_fn("No annotations stored.")
        return
    for expr, entries in all_data.items():
        print_fn(f"{expr} — {_describe(expr)} ({len(entries)} annotation(s))")
        for i, entry in enumerate(entries):
            author_str = f" [{entry['author']}]" if entry.get("author") else ""
            print_fn(f"  [{i}]{author_str} {entry['text']}")
