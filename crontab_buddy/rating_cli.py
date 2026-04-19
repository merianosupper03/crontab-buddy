"""CLI commands for rating cron expressions."""

from crontab_buddy.rating import rate_expression, get_rating, delete_rating, list_ratings
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _describe(expr_str):
    try:
        return humanize(CronExpression(expr_str))
    except CronParseError:
        return "(invalid expression)"


def cmd_rate_set(args, out=print):
    score = args.score
    expr = args.expression
    try:
        rate_expression(expr, score, path=getattr(args, 'rating_path', None))
        out(f"Saved rating {score}/5 for: {expr}")
    except ValueError as e:
        out(f"Error: {e}")


def cmd_rate_get(args, out=print):
    expr = args.expression
    entry = get_rating(expr, path=getattr(args, 'rating_path', None))
    if entry is None:
        out(f"No rating found for: {expr}")
    else:
        out(f"{expr}  [{entry['score']}/5]  {_describe(expr)}")
        if entry.get('note'):
            out(f"  Note: {entry['note']}")


def cmd_rate_delete(args, out=print):
    expr = args.expression
    removed = delete_rating(expr, path=getattr(args, 'rating_path', None))
    if removed:
        out(f"Deleted rating for: {expr}")
    else:
        out(f"No rating found for: {expr}")


def cmd_rate_list(args, out=print):
    ratings = list_ratings(path=getattr(args, 'rating_path', None))
    if not ratings:
        out("No ratings stored.")
        return
    for expr_str, entry in sorted(ratings.items(), key=lambda x: -x[1]['score']):
        out(f"{entry['score']}/5  {expr_str}  — {_describe(expr_str)}")
