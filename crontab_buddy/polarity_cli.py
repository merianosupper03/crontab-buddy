"""CLI commands for polarity assessment."""

import json
from crontab_buddy.polarity import assess_polarity, batch_polarity


def cmd_polarity_check(args):
    """Print full polarity summary for an expression."""
    result = assess_polarity(args.expression)
    print(str(result))


def cmd_polarity_score(args):
    """Print just the numeric polarity score."""
    result = assess_polarity(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.score)


def cmd_polarity_label(args):
    """Print just the polarity label (daytime/nighttime/neutral/all-day)."""
    result = assess_polarity(args.expression)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.polarity)


def cmd_polarity_batch(args):
    """Assess polarity for multiple space-separated expressions."""
    expressions = args.expressions
    results = batch_polarity(expressions)
    for r in results:
        print(str(r))


def cmd_polarity_json(args):
    """Output polarity result as JSON."""
    result = assess_polarity(args.expression)
    data = {
        "expression": result.expression,
        "polarity": result.polarity,
        "day_hours": result.day_hours,
        "night_hours": result.night_hours,
        "score": result.score,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
