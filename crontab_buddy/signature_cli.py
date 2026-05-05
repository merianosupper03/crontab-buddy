"""CLI commands for the signature feature."""

from crontab_buddy.signature import (
    compute_signature,
    save_signature,
    get_signature,
    verify_signature,
    delete_signature,
    list_signatures,
)


def _describe(entry: dict) -> str:
    label = entry.get("label") or "(no label)"
    return f"{entry['sig']}  {entry['expression']}  [{label}]"


def cmd_signature_compute(args) -> None:
    """Print the signature for an expression without saving it."""
    sig = compute_signature(args.expression)
    print(f"Signature: {sig}")


def cmd_signature_save(args) -> None:
    """Compute and save the signature for an expression."""
    label = getattr(args, "label", None)
    sig = save_signature(args.expression, label=label)
    print(f"Saved signature: {sig}")


def cmd_signature_get(args) -> None:
    """Retrieve a stored signature entry by its digest."""
    entry = get_signature(args.sig)
    if entry is None:
        print(f"No entry found for signature: {args.sig}")
    else:
        print(_describe({"sig": args.sig, **entry}))


def cmd_signature_verify(args) -> None:
    """Check whether an expression matches a given signature."""
    if verify_signature(args.expression, args.sig):
        print("OK: expression matches signature.")
    else:
        print("MISMATCH: expression does not match signature.")


def cmd_signature_delete(args) -> None:
    """Remove a stored signature entry."""
    if delete_signature(args.sig):
        print(f"Deleted signature: {args.sig}")
    else:
        print(f"Signature not found: {args.sig}")


def cmd_signature_list(args) -> None:
    """List all stored signatures."""
    entries = list_signatures()
    if not entries:
        print("No signatures stored.")
        return
    for entry in entries:
        print(_describe(entry))
