"""Compare two cron expressions side-by-side with field-level annotations."""

from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.humanizer import humanize

FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]


def compare(expr_a: str, expr_b: str) -> dict:
    """Return a structured comparison of two cron expression strings."""
    result = {
        "expr_a": expr_a,
        "expr_b": expr_b,
        "valid_a": True,
        "valid_b": True,
        "error_a": None,
        "error_b": None,
        "description_a": None,
        "description_b": None,
        "fields": [],
        "identical": False,
    }

    try:
        parsed_a = CronExpression(expr_a)
        result["description_a"] = humanize(parsed_a)
        fields_a = [parsed_a.minute, parsed_a.hour, parsed_a.dom, parsed_a.month, parsed_a.dow]
    except CronParseError as e:
        result["valid_a"] = False
        result["error_a"] = str(e)
        fields_a = None

    try:
        parsed_b = CronExpression(expr_b)
        result["description_b"] = humanize(parsed_b)
        fields_b = [parsed_b.minute, parsed_b.hour, parsed_b.dom, parsed_b.month, parsed_b.dow]
    except CronParseError as e:
        result["valid_b"] = False
        result["error_b"] = str(e)
        fields_b = None

    if fields_a and fields_b:
        all_same = True
        for name, fa, fb in zip(FIELD_NAMES, fields_a, fields_b):
            changed = fa != fb
            if changed:
                all_same = False
            result["fields"].append({
                "name": name,
                "value_a": fa,
                "value_b": fb,
                "changed": changed,
            })
        result["identical"] = all_same

    return result


def format_compare(result: dict) -> str:
    """Return a human-readable string from a compare() result dict."""
    lines = []
    lines.append(f"A: {result['expr_a']}")
    if result["error_a"]:
        lines.append(f"   ERROR: {result['error_a']}")
    else:
        lines.append(f"   {result['description_a']}")

    lines.append(f"B: {result['expr_b']}")
    if result["error_b"]:
        lines.append(f"   ERROR: {result['error_b']}")
    else:
        lines.append(f"   {result['description_b']}")

    if result["fields"]:
        lines.append("")
        lines.append("Field differences:")
        any_diff = False
        for f in result["fields"]:
            if f["changed"]:
                any_diff = True
                lines.append(f"  {f['name']:8s}  {f['value_a']:>10s}  ->  {f['value_b']}")
        if not any_diff:
            lines.append("  (no differences)")

    return "\n".join(lines)
