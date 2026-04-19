"""Batch processing: validate/describe multiple cron expressions at once."""

from typing import List, Dict, Any
from .parser import CronExpression, CronParseError
from .humanizer import humanize
from .validator import validate


def process_expressions(expressions: List[str]) -> List[Dict[str, Any]]:
    """Process a list of cron expression strings and return results for each."""
    results = []
    for raw in expressions:
        entry: Dict[str, Any] = {"expression": raw}
        try:
            expr = CronExpression(raw)
            vr = validate(expr)
            entry["valid"] = bool(vr)
            entry["errors"] = vr.errors
            entry["description"] = humanize(expr)
        except CronParseError as e:
            entry["valid"] = False
            entry["errors"] = [str(e)]
            entry["description"] = None
        results.append(entry)
    return results


def batch_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a high-level summary of batch processing results."""
    total = len(results)
    valid = sum(1 for r in results if r["valid"])
    return {
        "total": total,
        "valid": valid,
        "invalid": total - valid,
    }


def load_expressions_from_file(path: str) -> List[str]:
    """Read cron expressions from a file (one per line, skip comments/blanks)."""
    expressions = []
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                expressions.append(stripped)
    return expressions
