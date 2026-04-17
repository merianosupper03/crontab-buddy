"""CLI entry point for crontab-buddy."""

import argparse
from datetime import datetime

from .parser import CronExpression, CronParseError
from .humanizer import humanize
from .scheduler import next_runs


def _print_next_runs(expr: CronExpression, count: int) -> None:
    runs = next_runs(expr, count=count)
    print(f"\nNext {count} scheduled run(s):")
    for i, run in enumerate(runs, 1):
        print(f"  {i}. {run.strftime('%Y-%m-%d %H:%M')}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="crontab-buddy",
        description="Build, validate, and preview cron expressions.",
    )
    parser.add_argument(
        "expression",
        nargs="?",
        help="Cron expression to parse (e.g. '*/5 * * * *')",
    )
    parser.add_argument(
        "-n", "--next",
        type=int,
        default=5,
        metavar="COUNT",
        help="Number of upcoming run times to display (default: 5)",
    )
    parser.add_argument(
        "--no-schedule",
        action="store_true",
        help="Skip showing next run times",
    )

    args = parser.parse_args()

    if not args.expression:
        parser.print_help()
        return

    try:
        expr = CronExpression(args.expression)
    except CronParseError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)

    print(f"Expression : {expr}")
    print(f"Description: {humanize(expr)}")

    if not args.no_schedule:
        _print_next_runs(expr, args.next)


if __name__ == "__main__":
    main()
