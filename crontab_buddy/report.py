"""Generate a summary report for a set of cron expressions."""

from typing import List, Dict, Any
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.humanizer import humanize
from crontab_buddy.lint import lint
from crontab_buddy.scheduler import next_runs
from datetime import datetime


def _safe_parse(expr: str):
    try:
        return CronExpression(expr)
    except CronParseError:
        return None


def build_report(expressions: List[str], count: int = 3) -> List[Dict[str, Any]]:
    """Build a report for each expression with description, lint hints, and next runs."""
    results = []
    for raw in expressions:
        entry: Dict[str, Any] = {"expression": raw}
        parsed = _safe_parse(raw)
        if parsed is None:
            entry["valid"] = False
            entry["description"] = None
            entry["hints"] = []
            entry["next_runs"] = []
        else:
            entry["valid"] = True
            entry["description"] = humanize(parsed)
            result = lint(raw)
            entry["hints"] = result.hints
            runs = next_runs(parsed, count=count, start=datetime.utcnow())
            entry["next_runs"] = [r.strftime("%Y-%m-%d %H:%M") for r in runs]
        results.append(entry)
    return results


def format_report(report: List[Dict[str, Any]]) -> str:
    """Format the report as a human-readable string."""
    lines = []
    for entry in report:
        lines.append(f"Expression : {entry['expression']}")
        if not entry["valid"]:
            lines.append("  Status   : INVALID")
        else:
            lines.append(f"  Status   : valid")
            lines.append(f"  Desc     : {entry['description']}")
            if entry["hints"]:
                for h in entry["hints"]:
                    lines.append(f"  Hint     : {h}")
            if entry["next_runs"]:
                lines.append(f"  Next runs: {', '.join(entry['next_runs'])}")
        lines.append("")
    return "\n".join(lines).rstrip()


def summary_stats(report: List[Dict[str, Any]]) -> Dict[str, int]:
    """Return basic counts from a built report.

    Returns a dict with:
      - total: number of expressions evaluated
      - valid: number of valid expressions
      - invalid: number of invalid expressions
      - with_hints: number of valid expressions that have at least one lint hint
    """
    total = len(report)
    valid = sum(1 for e in report if e["valid"])
    with_hints = sum(1 for e in report if e["valid"] and e["hints"])
    return {
        "total": total,
        "valid": valid,
        "invalid": total - valid,
        "with_hints": with_hints,
    }
