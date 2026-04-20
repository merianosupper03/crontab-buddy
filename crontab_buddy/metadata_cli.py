"""CLI commands for managing expression metadata."""

from crontab_buddy.metadata import (
    set_metadata,
    get_metadata,
    get_all_metadata,
    delete_metadata,
    clear_metadata,
    list_all_metadata,
)


def cmd_metadata_set(args) -> None:
    """Set a metadata key/value for an expression."""
    set_metadata(args.expression, args.key, args.value, path=args.path)
    print(f"Metadata set: {args.key} = {args.value!r} for '{args.expression}'")


def cmd_metadata_get(args) -> None:
    """Get a metadata value by key."""
    value = get_metadata(args.expression, args.key, path=args.path)
    if value is None:
        print(f"No metadata key '{args.key}' for '{args.expression}'")
    else:
        print(f"{args.key}: {value!r}")


def cmd_metadata_list(args) -> None:
    """List all metadata for an expression."""
    meta = get_all_metadata(args.expression, path=args.path)
    if not meta:
        print(f"No metadata stored for '{args.expression}'")
        return
    print(f"Metadata for '{args.expression}':")
    for k, v in meta.items():
        print(f"  {k}: {v!r}")


def cmd_metadata_delete(args) -> None:
    """Delete a single metadata key."""
    removed = delete_metadata(args.expression, args.key, path=args.path)
    if removed:
        print(f"Deleted metadata key '{args.key}' from '{args.expression}'")
    else:
        print(f"Key '{args.key}' not found for '{args.expression}'")


def cmd_metadata_clear(args) -> None:
    """Clear all metadata for an expression."""
    removed = clear_metadata(args.expression, path=args.path)
    if removed:
        print(f"Cleared all metadata for '{args.expression}'")
    else:
        print(f"No metadata found for '{args.expression}'")


def cmd_metadata_all(args) -> None:
    """List all stored metadata across all expressions."""
    all_meta = list_all_metadata(path=args.path)
    if not all_meta:
        print("No metadata stored.")
        return
    for expr, meta in all_meta.items():
        print(f"{expr}:")
        for k, v in meta.items():
            print(f"  {k}: {v!r}")
