"""CLI commands for batch processing cron expressions."""

import json
from .batch import process_expressions, batch_summary, load_expressions_from_file


def cmd_batch_validate(args):
    """Validate a list of expressions passed as CLI args."""
    results = process_expressions(args.expressions)
    for r in results:
        status = "OK" if r["valid"] else "FAIL"
        print(f"[{status}] {r['expression']}")
        if r["description"]:
            print(f"       {r['description']}")
        for err in r["errors"]:
            print(f"       ERROR: {err}")
    summary = batch_summary(results)
    print(f"\nTotal: {summary['total']}  Valid: {summary['valid']}  Invalid: {summary['invalid']}")


def cmd_batch_file(args):
    """Load expressions from a file and validate/describe them."""
    try:
        expressions = load_expressions_from_file(args.file)
    except FileNotFoundError:
        print(f"File not found: {args.file}")
        return
    results = process_expressions(expressions)
    for r in results:
        status = "OK" if r["valid"] else "FAIL"
        print(f"[{status}] {r['expression']}")
        if r["description"]:
            print(f"       {r['description']}")
        for err in r["errors"]:
            print(f"       ERROR: {err}")
    summary = batch_summary(results)
    print(f"\nTotal: {summary['total']}  Valid: {summary['valid']}  Invalid: {summary['invalid']}")


def cmd_batch_json(args):
    """Output batch results as JSON."""
    if hasattr(args, 'file') and args.file:
        try:
            expressions = load_expressions_from_file(args.file)
        except FileNotFoundError:
            print(json.dumps({"error": f"File not found: {args.file}"}))
            return
    else:
        expressions = args.expressions
    results = process_expressions(expressions)
    summary = batch_summary(results)
    print(json.dumps({"summary": summary, "results": results}, indent=2))
