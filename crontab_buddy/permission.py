"""Permission management for cron expressions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_VALID_ROLES = {"owner", "editor", "viewer"}
_PERMISSIONS_FILE = Path.home() / ".crontab_buddy" / "permissions.json"


def _load() -> Dict[str, Dict[str, str]]:
    if _PERMISSIONS_FILE.exists():
        return json.loads(_PERMISSIONS_FILE.read_text())
    return {}


def _save(data: Dict[str, Dict[str, str]]) -> None:
    _PERMISSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PERMISSIONS_FILE.write_text(json.dumps(data, indent=2))


def set_permission(expression: str, user: str, role: str) -> None:
    """Assign a role to a user for the given expression."""
    if role not in _VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Must be one of: {sorted(_VALID_ROLES)}")
    data = _load()
    if expression not in data:
        data[expression] = {}
    data[expression][user] = role
    _save(data)


def get_permission(expression: str, user: str) -> Optional[str]:
    """Return the role assigned to a user for an expression, or None."""
    data = _load()
    return data.get(expression, {}).get(user)


def delete_permission(expression: str, user: str) -> bool:
    """Remove a user's permission for an expression. Returns True if removed."""
    data = _load()
    if expression in data and user in data[expression]:
        del data[expression][user]
        if not data[expression]:
            del data[expression]
        _save(data)
        return True
    return False


def get_all_permissions(expression: str) -> Dict[str, str]:
    """Return all user→role mappings for an expression."""
    return dict(_load().get(expression, {}))


def list_users_with_role(role: str) -> List[Dict[str, str]]:
    """Return all (expression, user) pairs that have the given role."""
    if role not in _VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'.")
    data = _load()
    results = []
    for expr, perms in data.items():
        for user, r in perms.items():
            if r == role:
                results.append({"expression": expr, "user": user})
    return results
