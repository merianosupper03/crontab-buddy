"""CLI commands for schedule dependency management."""
from __future__ import annotations

from crontab_buddy.dependency import (
    add_dependency,
    clear_dependencies,
    get_dependencies,
    list_all_dependencies,
    remove_dependency,
)


def cmd_dep_add(args) -> None:
    """Add a dependency between two named schedules."""
    ok = add_dependency(args.schedule, args.depends_on)
    if ok:
        print(f"Dependency added: '{args.schedule}' depends on '{args.depends_on}'")
    else:
        print(f"'{args.schedule}' already depends on '{args.depends_on}'")


def cmd_dep_remove(args) -> None:
    """Remove a dependency."""
    ok = remove_dependency(args.schedule, args.depends_on)
    if ok:
        print(f"Removed dependency: '{args.schedule}' no longer depends on '{args.depends_on}'")
    else:
        print(f"No such dependency: '{args.schedule}' -> '{args.depends_on}'")


def cmd_dep_list(args) -> None:
    """List dependencies for a given schedule."""
    deps = get_dependencies(args.schedule)
    if not deps:
        print(f"No dependencies for '{args.schedule}'")
        return
    print(f"Dependencies for '{args.schedule}':")
    for dep in deps:
        print(f"  - {dep}")


def cmd_dep_list_all(args) -> None:  # noqa: ARG001
    """List all dependency relationships."""
    all_deps = list_all_dependencies()
    if not all_deps:
        print("No dependencies recorded.")
        return
    for schedule, deps in sorted(all_deps.items()):
        print(f"{schedule}:")
        for dep in deps:
            print(f"  -> {dep}")


def cmd_dep_clear(args) -> None:
    """Clear all dependencies for a schedule."""
    clear_dependencies(args.schedule)
    print(f"Cleared all dependencies for '{args.schedule}'")
