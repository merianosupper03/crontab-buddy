"""CLI helpers for the tagging feature."""

from typing import Optional
from crontab_buddy.tags import (
    add_tag, remove_tag, get_tags, find_by_tag, list_all_tags
)


def _build_kwargs(path: Optional[str]) -> dict:
    return {"path": path} if path else {}


def cmd_tag_add(expression: str, tag: str, path: Optional[str] = None) -> None:
    add_tag(expression, tag, **_build_kwargs(path))
    print(f"Tagged '{expression}' with '{tag}'.")


def cmd_tag_remove(expression: str, tag: str, path: Optional[str] = None) -> None:
    removed = remove_tag(expression, tag, **_build_kwargs(path))
    if removed:
        print(f"Removed tag '{tag}' from '{expression}'.")
    else:
        print(f"Tag '{tag}' not found on '{expression}'.")


def cmd_tag_list(expression: str, path: Optional[str] = None) -> None:
    tags = get_tags(expression, **_build_kwargs(path))
    if tags:
        print(f"Tags for '{expression}': {', '.join(tags)}")
    else:
        print(f"No tags found for '{expression}'.")


def cmd_tag_find(tag: str, path: Optional[str] = None) -> None:
    expressions = find_by_tag(tag, **_build_kwargs(path))
    if expressions:
        print(f"Expressions tagged '{tag}':")
        for expr in expressions:
            print(f"  {expr}")
    else:
        print(f"No expressions found with tag '{tag}'.")


def cmd_tag_all(path: Optional[str] = None) -> None:
    all_tags = list_all_tags(**_build_kwargs(path))
    if not all_tags:
        print("No tags saved.")
        return
    for expr, tags in all_tags.items():
        print(f"  {expr}: {', '.join(tags)}")
