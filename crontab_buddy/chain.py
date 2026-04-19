"""Chain multiple cron expressions together with labels and intervals."""

from typing import List, Dict, Optional
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.humanizer import humanize


def _safe_humanize(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except CronParseError:
        return "(invalid)"


def build_chain(entries: List[Dict]) -> List[Dict]:
    """Validate and enrich a list of chain entries.

    Each entry should have:
      - 'expression': cron string
      - 'label': optional human label

    Returns enriched list with 'valid', 'description', and 'error' keys.
    """
    result = []
    for i, entry in enumerate(entries):
        expr_str = entry.get("expression", "")
        label = entry.get("label") or f"step-{i + 1}"
        item: Dict = {"index": i, "label": label, "expression": expr_str}
        try:
            expr = CronExpression(expr_str)
            item["valid"] = True
            item["description"] = humanize(expr)
            item["error"] = None
        except CronParseError as e:
            item["valid"] = False
            item["description"] = "(invalid)"
            item["error"] = str(e)
        result.append(item)
    return result


def format_chain(chain: List[Dict]) -> str:
    """Return a human-readable multi-line summary of a chain."""
    if not chain:
        return "(empty chain)"
    lines = []
    for item in chain:
        status = "OK" if item["valid"] else "FAIL"
        label = item["label"]
        expr = item["expression"]
        desc = item["description"]
        line = f"[{status}] {label}: {expr}  →  {desc}"
        if item["error"]:
            line += f"  [!] {item['error']}"
        lines.append(line)
    return "\n".join(lines)


def chain_valid(chain: List[Dict]) -> bool:
    """Return True only if every entry in the chain is valid."""
    return all(item["valid"] for item in chain)
