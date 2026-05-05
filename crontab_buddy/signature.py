"""Signature module: generate and verify deterministic fingerprints for cron expressions."""

import hashlib
import json
import os
from typing import Optional

_DEFAULT_PATH = os.path.expanduser("~/.crontab_buddy_signatures.json")


def _load(path: str = _DEFAULT_PATH) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def _save(data: dict, path: str = _DEFAULT_PATH) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def compute_signature(expression: str) -> str:
    """Return a short SHA-256 hex digest for the given cron expression."""
    return hashlib.sha256(expression.strip().encode()).hexdigest()[:16]


def save_signature(expression: str, label: Optional[str] = None,
                   path: str = _DEFAULT_PATH) -> str:
    """Compute and persist the signature for an expression. Returns the signature."""
    sig = compute_signature(expression)
    data = _load(path)
    data[sig] = {"expression": expression.strip(), "label": label or ""}
    _save(data, path)
    return sig


def get_signature(sig: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Look up a stored signature entry by its hex digest."""
    return _load(path).get(sig)


def verify_signature(expression: str, sig: str) -> bool:
    """Return True if the given expression matches the provided signature."""
    return compute_signature(expression) == sig


def delete_signature(sig: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove a signature entry. Returns True if it existed."""
    data = _load(path)
    if sig not in data:
        return False
    del data[sig]
    _save(data, path)
    return True


def list_signatures(path: str = _DEFAULT_PATH) -> list:
    """Return all stored signature entries as a list of dicts."""
    data = _load(path)
    return [{"sig": k, **v} for k, v in data.items()]
