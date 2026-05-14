"""CLI commands for texture analysis."""
from __future__ import annotations
import json
from crontab_buddy.texture import assess_texture, batch_texture


def cmd_texture_check(args) -> None:
    result = assess_texture(args.expression)
    print(f"Expression : {result.expression}")
    if result.error:
        print(f"Error      : {result.error}")
        return
    print(f"Score      : {result.score:.4f}")
    print(f"Grade      : {result.grade}")
    for field_name, s in result.scores.items():
        print(f"  {field_name:<8}: {s:.4f}")


def cmd_texture_score(args) -> None:
    result = assess_texture(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.score)


def cmd_texture_grade(args) -> None:
    result = assess_texture(args.expression)
    if result.error:
        print(f"error: {result.error}")
    else:
        print(result.grade)


def cmd_texture_batch(args) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    results = batch_texture(expressions)
    for r in results:
        if r.error:
            print(f"{r.expression!r:40s}  error: {r.error}")
        else:
            print(f"{r.expression!r:40s}  score={r.score:.4f}  grade={r.grade}")


def cmd_texture_json(args) -> None:
    result = assess_texture(args.expression)
    payload = {
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "scores": result.scores,
        "error": result.error,
    }
    print(json.dumps(payload, indent=2))
