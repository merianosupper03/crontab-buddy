"""CLI commands for bulk import/export of cron expressions to/from JSON or text files."""

import json
from crontab_buddy.exporter import to_crontab_line, to_json_dict
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.favorites import save_favorite, list_favorites


def cmd_export_favorites(args, out=print):
    """Export all favorites to JSON or crontab format."""
    favs = list_favorites(path=getattr(args, 'fav_path', None))
    if not favs:
        out("No favorites to export.")
        return

    fmt = getattr(args, 'format', 'json')
    if fmt == 'crontab':
        for name, expr_str in favs.items():
            try:
                expr = CronExpression(expr_str)
                out(to_crontab_line(expr, comment=name))
            except CronParseError:
                out(f"# invalid: {expr_str}  ({name})")
    else:
        records = []
        for name, expr_str in favs.items():
            try:
                expr = CronExpression(expr_str)
                records.append({"name": name, **to_json_dict(expr)})
            except CronParseError:
                records.append({"name": name, "expression": expr_str, "error": "invalid"})
        out(json.dumps(records, indent=2))


def cmd_import_favorites(args, out=print):
    """Import favorites from a JSON file produced by export."""
    path = args.file
    try:
        with open(path) as f:
            records = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        out(f"Error reading file: {e}")
        return

    imported = 0
    for rec in records:
        name = rec.get("name")
        expr_str = rec.get("expression")
        if not name or not expr_str:
            out(f"Skipping invalid record: {rec}")
            continue
        try:
            CronExpression(expr_str)
            save_favorite(name, expr_str, path=getattr(args, 'fav_path', None))
            out(f"Imported: {name} -> {expr_str}")
            imported += 1
        except CronParseError as e:
            out(f"Skipping '{name}' ({expr_str}): {e}")

    out(f"\nDone. {imported} favorite(s) imported.")
