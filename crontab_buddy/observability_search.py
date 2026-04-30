"""Search observability configs by expression or settings."""

from typing import List, Dict, Any
from crontab_buddy.observability import list_observability
from crontab_buddy.humanizer import humanize
from crontab_buddy.parser import CronExpression, CronParseError


def _safe_humanize(expression: str) -> str:
    try:
        return humanize(CronExpression(expression))
    except CronParseError:
        return ""


def search_observability(
    query: str,
    path: str = None,
    match_log_level: str = None,
    match_trace: str = None,
    metrics_only: bool = False,
) -> List[Dict[str, Any]]:
    """Search observability configs by expression, description, or settings.

    Args:
        query: Substring to match against expression or humanized description.
        path: Optional custom storage path.
        match_log_level: Filter by exact log level if provided.
        match_trace: Filter by exact trace backend if provided.
        metrics_only: If True, only return entries with metrics enabled.

    Returns:
        List of matching result dicts with keys: expression, config, description.
    """
    kwargs = {} if path is None else {"path": path}
    all_configs = list_observability(**kwargs)
    results = []
    query_lower = query.lower()

    for expr, cfg in all_configs.items():
        description = _safe_humanize(expr)
        if query_lower not in expr.lower() and query_lower not in description.lower():
            continue
        if match_log_level and cfg.get("log_level") != match_log_level:
            continue
        if match_trace and cfg.get("trace_backend") != match_trace:
            continue
        if metrics_only and not cfg.get("metrics_enabled", False):
            continue
        results.append({"expression": expr, "config": cfg, "description": description})

    return results
