"""CLI commands for topology analysis."""

import json
from crontab_buddy.topology import assess_topology


def cmd_topology_check(args, print_fn=print):
    """Print a full topology report for an expression."""
    result = assess_topology(args.expression)
    print_fn(f"Expression : {result.expression}")
    if result.error:
        print_fn(f"Error      : {result.error}")
        return
    print_fn(f"Score      : {result.score:.3f}")
    print_fn(f"Grade      : {result.grade}")
    print_fn("Fields:")
    for name, score in result.field_scores.items():
        bar = "#" * int(score * 10)
        print_fn(f"  {name:<8} {score:.2f}  [{bar:<10}]")


def cmd_topology_score(args, print_fn=print):
    """Print only the topology score."""
    result = assess_topology(args.expression)
    if result.error:
        print_fn(f"Error: {result.error}")
        return
    print_fn(f"{result.score:.4f}")


def cmd_topology_grade(args, print_fn=print):
    """Print only the topology grade label."""
    result = assess_topology(args.expression)
    if result.error:
        print_fn(f"Error: {result.error}")
        return
    print_fn(result.grade)


def cmd_topology_batch(args, print_fn=print):
    """Check topology for multiple space-separated expressions."""
    expressions = args.expressions
    for expr_str in expressions:
        result = assess_topology(expr_str)
        if result.error:
            print_fn(f"{expr_str!r:30s}  ERROR: {result.error}")
        else:
            print_fn(f"{expr_str!r:30s}  {result.score:.3f}  {result.grade}")


def cmd_topology_json(args, print_fn=print):
    """Output topology result as JSON."""
    result = assess_topology(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "field_scores": result.field_scores,
        "error": result.error,
    }
    print_fn(json.dumps(data, indent=2))
