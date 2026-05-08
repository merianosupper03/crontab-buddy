"""CLI commands for tempo assessment."""
from crontab_buddy.tempo import assess_tempo, batch_tempo
import json


def cmd_tempo_check(args, print_fn=print):
    """Print full tempo assessment for an expression."""
    result = assess_tempo(args.expression)
    print_fn(f"Expression : {result.expression}")
    if result.error:
        print_fn(f"Error      : {result.error}")
        return
    print_fn(f"Level      : {result.level}")
    print_fn(f"Score      : {result.score:.3f}")
    if result.interval_seconds is not None:
        print_fn(f"Interval   : {result.interval_seconds}s")


def cmd_tempo_level(args, print_fn=print):
    """Print only the tempo level."""
    result = assess_tempo(args.expression)
    print_fn(result.level)


def cmd_tempo_score(args, print_fn=print):
    """Print only the tempo score."""
    result = assess_tempo(args.expression)
    print_fn(f"{result.score:.3f}")


def cmd_tempo_batch(args, print_fn=print):
    """Assess tempo for multiple space-separated expressions."""
    expressions = args.expressions
    results = batch_tempo(expressions)
    for r in results:
        if r.error:
            print_fn(f"{r.expression!r:40s}  ERROR: {r.error}")
        else:
            print_fn(f"{r.expression!r:40s}  {r.level:10s}  {r.score:.3f}")


def cmd_tempo_json(args, print_fn=print):
    """Output tempo assessment as JSON."""
    result = assess_tempo(args.expression)
    data = {
        "expression": result.expression,
        "level": result.level,
        "score": result.score,
        "interval_seconds": result.interval_seconds,
        "error": result.error,
    }
    print_fn(json.dumps(data, indent=2))
