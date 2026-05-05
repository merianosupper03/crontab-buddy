"""Execution tracing — record and retrieve trace spans for cron expressions."""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_traces.json")


def _load(path: str = _DEFAULT_PATH) -> Dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save(data: Dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def start_trace(
    expression: str,
    label: Optional[str] = None,
    path: str = _DEFAULT_PATH,
) -> str:
    """Begin a new trace span for *expression*. Returns the trace ID."""
    data = _load(path)
    trace_id = uuid.uuid4().hex[:12]
    entry = {
        "trace_id": trace_id,
        "expression": expression,
        "label": label,
        "started_at": time.time(),
        "finished_at": None,
        "duration_ms": None,
        "status": "running",
    }
    data.setdefault(expression, []).append(entry)
    _save(data, path)
    return trace_id


def finish_trace(
    expression: str,
    trace_id: str,
    status: str = "ok",
    path: str = _DEFAULT_PATH,
) -> bool:
    """Close an open trace span. Returns True if found and updated."""
    valid = {"ok", "fail", "timeout"}
    if status not in valid:
        raise ValueError(f"status must be one of {valid}")
    data = _load(path)
    for entry in data.get(expression, []):
        if entry["trace_id"] == trace_id and entry["status"] == "running":
            now = time.time()
            entry["finished_at"] = now
            entry["duration_ms"] = round((now - entry["started_at"]) * 1000, 2)
            entry["status"] = status
            _save(data, path)
            return True
    return False


def get_traces(
    expression: str, path: str = _DEFAULT_PATH
) -> List[Dict]:
    """Return all trace spans for *expression*, newest first."""
    data = _load(path)
    spans = data.get(expression, [])
    return sorted(spans, key=lambda s: s["started_at"], reverse=True)


def clear_traces(expression: str, path: str = _DEFAULT_PATH) -> None:
    """Delete all traces for *expression*."""
    data = _load(path)
    data.pop(expression, None)
    _save(data, path)


def list_traced_expressions(path: str = _DEFAULT_PATH) -> List[str]:
    return list(_load(path).keys())
