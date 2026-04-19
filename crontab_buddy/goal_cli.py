"""CLI commands for goal tracking."""

from crontab_buddy import goal as _goal
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return "(invalid expression)"


def cmd_goal_set(args, path=_goal.DEFAULT_PATH) -> None:
    try:
        _goal.set_goal(args.expression, args.target, getattr(args, "note", ""), path=path)
        print(f"Goal set: {args.expression} → {args.target} runs")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_goal_run(args, path=_goal.DEFAULT_PATH) -> None:
    count = _goal.record_run(args.expression, path=path)
    g = _goal.get_goal(args.expression, path=path)
    target = g["target"] if g else "?"
    print(f"Recorded run for {args.expression}. Count: {count}/{target}")


def cmd_goal_get(args, path=_goal.DEFAULT_PATH) -> None:
    g = _goal.get_goal(args.expression, path=path)
    if g is None:
        print(f"No goal set for: {args.expression}")
        return
    pct = (g["count"] / g["target"] * 100) if g["target"] else 0
    print(f"Expression : {args.expression}")
    print(f"Description: {_describe(args.expression)}")
    print(f"Progress   : {g['count']}/{g['target']} ({pct:.1f}%)")
    if g.get("note"):
        print(f"Note       : {g['note']}")


def cmd_goal_delete(args, path=_goal.DEFAULT_PATH) -> None:
    if _goal.delete_goal(args.expression, path=path):
        print(f"Deleted goal for: {args.expression}")
    else:
        print(f"No goal found for: {args.expression}")


def cmd_goal_list(args, path=_goal.DEFAULT_PATH) -> None:
    goals = _goal.list_goals(path=path)
    if not goals:
        print("No goals set.")
        return
    for g in goals:
        pct = (g["count"] / g["target"] * 100) if g["target"] else 0
        bar = "#" * int(pct // 10) + "-" * (10 - int(pct // 10))
        print(f"[{bar}] {g['count']}/{g['target']} {g['expression']}")
