"""CLI helpers for the tagging feature."""

from typing import Optional
from crontab_buddy.tags import (
    add_tag, remove_tag, get_tags, find_by_tag, list_all_tags
)


def cmd_tag_add(expression: str, tag: str, path: Optional[str] = None) -> None:
    kwargs = {"path": path} if path else {}
    add_tag(expression, tag, **kwargs)
    print(f"Tagged '{expression}' with '{tag}'.")


def cmd_tag_remove(expression: str, tag: str, path: Optional[str] = None) -> None:
    kwargs = {"path": path} if path else {}
    removed = remove_tag(expression, tag, **kwargs)
    if removed:
        print(f"Removed tag '{tag}' from '{expression}'.")
    else:
        print(f"Tag '{tag}' not found on '{expression}'.")


def cmd_tag_list(expression: str, path: Optional[str] = None) -> None:
    kwargs = {"path": path} if path else {}
    tags = get_tags(expression, **kwargs)
    if tags:
        print(f"Tags for '{expression}': {', '.join(tags)}")
    else:
        print(f"No tags found for '{expression}'.")


def cmd_tag_find(tag: str, path: Optional[str] = None) -> None:
    kwargs = {"path": path} if path else {}
    expressions = find_by_tag(tag, **kwargs)
    if expressions:
        print(f"Expressions tagged '{tag}':")
        for expr in expressions:
            print(f"  {expr}")
    else:
        print(f"No expressions found with tag '{tag}'.")


def cmd_tag_all(path: Optional[str] = None) -> None:
    kwargs = {"path": path} if path else {}
    all_tags = list_all_tags(**kwargs)
    if not all_tags:
        print("No tags saved.")
        return
    for expr, tags in all_tags.items():
        print(f"  {expr}: {', '.join(tags)}")
