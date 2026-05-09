"""CLI commands for resonance analysis."""

import json
from crontab_buddy.resonance import assess_resonance, batch_resonance


def cmd_resonance_check(args):
    result = assess_resonance(args.expr_a, args.expr_b)
    print(f"Expression A : {result.expression_a}")
    print(f"Expression B : {result.expression_b}")
    if result.error:
        print(f"Error        : {result.error}")
        return
    print(f"Grade        : {result.grade}")
    print(f"Score        : {result.score:.4f}")
    print(f"Shared mins  : {result.shared_minutes}")
    print(f"Total mins   : {result.total_minutes}")


def cmd_resonance_score(args):
    result = assess_resonance(args.expr_a, args.expr_b)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.score)


def cmd_resonance_grade(args):
    result = assess_resonance(args.expr_a, args.expr_b)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(result.grade)


def cmd_resonance_batch(args):
    others = [e.strip() for e in args.others.split(",") if e.strip()]
    results = batch_resonance(args.expr_a, others)
    for r in results:
        if r.error:
            print(f"  {r.expression_b:<25} ERROR: {r.error}")
        else:
            print(f"  {r.expression_b:<25} {r.grade:<12} {r.score:.4f}")


def cmd_resonance_json(args):
    result = assess_resonance(args.expr_a, args.expr_b)
    data = {
        "expression_a": result.expression_a,
        "expression_b": result.expression_b,
        "score": result.score,
        "grade": result.grade,
        "shared_minutes": result.shared_minutes,
        "total_minutes": result.total_minutes,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
