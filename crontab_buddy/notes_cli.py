"""CLI commands for managing cron expression notes."""

from crontab_buddy.notes import set_note, get_note, delete_note, list_notes


def cmd_note_set(expression: str, note: str, path: str = None) -> None:
    kwargs = {"path": path} if path else {}
    set_note(expression, note, **kwargs)
    print(f"Note saved for '{expression}'.")


def cmd_note_get(expression: str, path: str = None) -> None:
    kwargs = {"path": path} if path else {}
    note = get_note(expression, **kwargs)
    if note is None:
        print(f"No note found for '{expression}'.")
    else:
        print(f"{expression}: {note}")


def cmd_note_delete(expression: str, path: str = None) -> None:
    kwargs = {"path": path} if path else {}
    removed = delete_note(expression, **kwargs)
    if removed:
        print(f"Note for '{expression}' deleted.")
    else:
        print(f"No note found for '{expression}'.")


def cmd_note_list(path: str = None) -> None:
    kwargs = {"path": path} if path else {}
    notes = list_notes(**kwargs)
    if not notes:
        print("No notes stored.")
        return
    for expr, note in notes.items():
        print(f"  {expr}: {note}")
