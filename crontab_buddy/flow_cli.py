"""CLI commands for flow analysis."""

from __future__ import annotations
import json
from crontab_buddy.flow import assess_flow, batch_flow


def cmd_flow_check(args) -> None:
    result = assess_flow(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Grade      : {result.grade}")
    print(f"Score      : {result.score:.4f}")
    print(f"Transitions: {result.transitions}")
    print(f"Gaps       : {result.total_gaps}")


def cmd_flow_score(args) -> None:
    result = assess_flow(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_flow_grade(args) -> None:
    result = assess_flow(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_flow_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_flow(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:30s}  error: {r.error}")
        else:
            print(f"{r.expression!r:30s}  {r.grade:10s}  {r.score:.4f}")


def cmd_flow_json(args) -> None:
    result = assess_flow(args.expression)
    data = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "transitions": result.transitions,
        "total_gaps": result.total_gaps,
        "error": result.error,
    }
    print(json.dumps(data, indent=2))
