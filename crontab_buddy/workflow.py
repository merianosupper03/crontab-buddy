"""Workflow: ordered sequence of named cron expressions with metadata."""

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".crontab_buddy" / "workflows.json"


def _load(path: Path = _DEFAULT_PATH) -> Dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save(data: Dict, path: Path = _DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def create_workflow(name: str, path: Path = _DEFAULT_PATH) -> bool:
    data = _load(path)
    key = name.lower()
    if key in data:
        return False
    data[key] = {"name": name, "steps": []}
    _save(data, path)
    return True


def add_step(name: str, expression: str, label: Optional[str] = None, path: Path = _DEFAULT_PATH) -> bool:
    data = _load(path)
    key = name.lower()
    if key not in data:
        return False
    step = {"expression": expression, "label": label or expression}
    data[key]["steps"].append(step)
    _save(data, path)
    return True


def remove_step(name: str, index: int, path: Path = _DEFAULT_PATH) -> bool:
    data = _load(path)
    key = name.lower()
    if key not in data:
        return False
    steps = data[key]["steps"]
    if index < 0 or index >= len(steps):
        return False
    steps.pop(index)
    _save(data, path)
    return True


def get_workflow(name: str, path: Path = _DEFAULT_PATH) -> Optional[Dict]:
    data = _load(path)
    return data.get(name.lower())


def delete_workflow(name: str, path: Path = _DEFAULT_PATH) -> bool:
    data = _load(path)
    key = name.lower()
    if key not in data:
        return False
    del data[key]
    _save(data, path)
    return True


def list_workflows(path: Path = _DEFAULT_PATH) -> List[Dict]:
    data = _load(path)
    return list(data.values())
