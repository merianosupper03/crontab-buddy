"""CLI commands for playlist management."""

from crontab_buddy.playlist import (
    create_playlist, add_to_playlist, remove_from_playlist,
    get_playlist, delete_playlist, list_playlists,
)
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except CronParseError:
        return "(invalid expression)"


def cmd_playlist_create(args, print_fn=print):
    if create_playlist(args.name, **_path_kw(args)):
        print_fn(f"Playlist '{args.name}' created.")
    else:
        print_fn(f"Playlist '{args.name}' already exists.")


def cmd_playlist_add(args, print_fn=print):
    ok = add_to_playlist(args.name, args.expression, **_path_kw(args))
    if ok:
        print_fn(f"Added '{args.expression}' to playlist '{args.name}'.")
    else:
        print_fn(f"Playlist '{args.name}' not found. Create it first.")


def cmd_playlist_remove(args, print_fn=print):
    ok = remove_from_playlist(args.name, args.expression, **_path_kw(args))
    if ok:
        print_fn(f"Removed '{args.expression}' from playlist '{args.name}'.")
    else:
        print_fn("Expression or playlist not found.")


def cmd_playlist_list(args, print_fn=print):
    entries = get_playlist(args.name, **_path_kw(args))
    if entries is None:
        print_fn(f"Playlist '{args.name}' not found.")
        return
    if not entries:
        print_fn(f"Playlist '{args.name}' is empty.")
        return
    for i, expr in enumerate(entries, 1):
        print_fn(f"{i}. {expr}  # {_describe(expr)}")


def cmd_playlist_delete(args, print_fn=print):
    if delete_playlist(args.name, **_path_kw(args)):
        print_fn(f"Playlist '{args.name}' deleted.")
    else:
        print_fn(f"Playlist '{args.name}' not found.")


def cmd_playlist_all(args, print_fn=print):
    names = list_playlists(**_path_kw(args))
    if not names:
        print_fn("No playlists found.")
    for name in names:
        print_fn(name)


def _path_kw(args):
    path = getattr(args, "path", None)
    return {"path": path} if path else {}
