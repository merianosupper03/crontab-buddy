"""Observability settings for cron expressions (tracing, metrics, logging level)."""

import json
import os
from typing import Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_observability.json")

VALID_LOG_LEVELS = {"debug", "info", "warning", "error", "none"}
VALID_TRACE_BACKENDS = {"jaeger", "zipkin", "otlp", "none"}


def _load(path: str = _DEFAULT_PATH) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_observability(
    expression: str,
    log_level: str = "info",
    trace_backend: str = "none",
    metrics_enabled: bool = False,
    path: str = _DEFAULT_PATH,
) -> None:
    """Set observability config for a cron expression."""
    if log_level not in VALID_LOG_LEVELS:
        raise ValueError(f"Invalid log_level '{log_level}'. Choose from {VALID_LOG_LEVELS}.")
    if trace_backend not in VALID_TRACE_BACKENDS:
        raise ValueError(f"Invalid trace_backend '{trace_backend}'. Choose from {VALID_TRACE_BACKENDS}.")
    data = _load(path)
    data[expression] = {
        "log_level": log_level,
        "trace_backend": trace_backend,
        "metrics_enabled": metrics_enabled,
    }
    _save(data, path)


def get_observability(expression: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Return observability config for the given expression, or None."""
    return _load(path).get(expression)


def delete_observability(expression: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove observability config. Returns True if it existed."""
    data = _load(path)
    if expression in data:
        del data[expression]
        _save(data, path)
        return True
    return False


def list_observability(path: str = _DEFAULT_PATH) -> dict:
    """Return all observability configs keyed by expression."""
    return _load(path)
