"""CLI entry point for crontab-buddy."""

import argparse
import json
from datetime import datetime

from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.humanizer import humanize
from crontab_buddy.scheduler import next_runs
from crontab_buddy.exporter import to_crontab_line, to_markdown, to_json_dict
from crontab_buddy.suggester import suggest, list_all


def _print_next_runs(expr: CronExpression, count: int = 5) -> None:
    runs = next_runs(expr, datetime.now(), count=count)
    print(f"Next {count} runs:")
    for r in runs:
        print(f"  {r.strftime('%Y-%m-%d %H:%M')}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="crontab-buddy",
        description="Build, validate, and document cron expressions.",
    )
    sub = parser.add_subparsers(dest="command")

    # explain
    exp_p = sub.add_parser("explain", help="Explain a cron expression")
    exp_p.add_argument("expression", help="Cron expression (5 fields)")
    exp_p.add_argument("--next", type=int, default=5, metavar="N", help="Show next N runs")
    exp_p.add_argument("--export", choices=["crontab", "markdown", "json"], default=None)
    exp_p.add_argument("--comment", default="", help="Optional comment for export")

    # suggest
    sug_p = sub.add_parser("suggest", help="Suggest cron expressions from a keyword")
    sug_p.add_argument("query", nargs="?", default="", help="Plain-English query")
    sug_p.add_argument("--list-all", action="store_true", help="List all built-in suggestions")
    sug_p.add_argument("--max", type=int, default=5)

    args = parser.parse_args()

    if args.command == "explain":
        try:
            expr = CronExpression(args.expression)
        except CronParseError as e:
            print(f"Error: {e}")
            raise SystemExit(1)

        print(f"Expression : {expr}")
        print(f"Description: {humanize(expr)}")

        if args.export == "crontab":
            print(to_crontab_line(expr, args.comment))
        elif args.export == "markdown":
            print(to_markdown(expr, args.comment))
        elif args.export == "json":
            print(json.dumps(to_json_dict(expr, args.comment), indent=2))
        else:
            _print_next_runs(expr, args.next)

    elif args.command == "suggest":
        if args.list_all:
            items = list_all()
        else:
            items = suggest(args.query, max_results=args.max)

        if not items:
            print("No suggestions found.")
        else:
            print(f"{'Expression':<20} Description")
            print("-" * 50)
            for expr_str, label in items:
                print(f"{expr_str:<20} {label}")
    else:
        parser.print_help()
