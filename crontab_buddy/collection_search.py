"""Search across collections by keyword."""
from typing import List, Dict
from crontab_buddy.collections import _load, get_collection
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.humanizer import humanize
from pathlib import Path

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "collections.json"


def _safe_humanize(expr: str) -> str:
    try:
        return humanize(CronExpression(expr))
    except CronParseError:
        return ""


def search_collections(keyword: str, path: Path = _DEFAULT_PATH) -> List[Dict]:
    """Search all collections for expressions matching keyword."""
    keyword = keyword.lower()
    data = _load(path)
    results = []
    for col_name, expressions in data.items():
        for expr in expressions:
            desc = _safe_humanize(expr)
            if keyword in expr.lower() or keyword in desc.lower() or keyword in col_name.lower():
                results.append({
                    "collection": col_name,
                    "expression": expr,
                    "description": desc,
                })
    return results
