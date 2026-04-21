"""CLI commands for the run log feature."""

from crontab_buddy.runlog import log_run, get_runs, clear_runs, list_all_runs


def _describe(entry: dict) -> str:
    ts = entry.get("timestamp", "?")
    status = entry.get("status", "?")
    msg = entry.get("message", "")
    line = f"[{ts}] {status.upper()}"
    if msg:
        line += f" — {msg}"
    return line


def cmd_runlog_add(args, path=None):
    kwargs = {"expression": args.expression, "status": args.status}
    if hasattr(args, "message") and args.message:
        kwargs["message"] = args.message
    if path:
        kwargs["path"] = path
    try:
        log_run(**kwargs)
        print(f"Logged {args.status} for '{args.expression}'.")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_runlog_get(args, path=None):
    kwargs = {"expression": args.expression}
    if hasattr(args, "limit") and args.limit:
        kwargs["limit"] = int(args.limit)
    if path:
        kwargs["path"] = path
    entries = get_runs(**kwargs)
    if not entries:
        print(f"No run log entries for '{args.expression}'.")
        return
    for entry in entries:
        print(_describe(entry))


def cmd_runlog_clear(args, path=None):
    kwargs = {"expression": args.expression}
    if path:
        kwargs["path"] = path
    clear_runs(**kwargs)
    print(f"Cleared run log for '{args.expression}'.")


def cmd_runlog_list(args, path=None):
    kwargs = {"path": path} if path else {}
    all_runs = list_all_runs(**kwargs)
    if not all_runs:
        print("Run log is empty.")
        return
    for expr, entries in all_runs.items():
        print(f"{expr} ({len(entries)} run(s))")
        for entry in reversed(entries[-3:]):
            print(f"  {_describe(entry)}")
