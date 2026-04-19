"""Tests for import_export_cli commands."""

import json
import pytest
from types import SimpleNamespace
from unittest.mock import patch
from crontab_buddy.import_export_cli import cmd_export_favorites, cmd_import_favorites


@pytest.fixture
def tmp_fav(tmp_path):
    return tmp_path / "favorites.json"


def args(**kwargs):
    return SimpleNamespace(**kwargs)


def test_export_no_favorites(tmp_fav):
    lines = []
    cmd_export_favorites(args(fav_path=str(tmp_fav), format='json'), out=lines.append)
    assert any("No favorites" in l for l in lines)


def test_export_json_format(tmp_fav):
    from crontab_buddy.favorites import save_favorite
    save_favorite("daily", "0 9 * * *", path=str(tmp_fav))
    lines = []
    cmd_export_favorites(args(fav_path=str(tmp_fav), format='json'), out=lines.append)
    combined = "\n".join(lines)
    data = json.loads(combined)
    assert any(r["name"] == "daily" for r in data)
    assert any(r["expression"] == "0 9 * * *" for r in data)


def test_export_crontab_format(tmp_fav):
    from crontab_buddy.favorites import save_favorite
    save_favorite("weekly", "0 0 * * 0", path=str(tmp_fav))
    lines = []
    cmd_export_favorites(args(fav_path=str(tmp_fav), format='crontab'), out=lines.append)
    combined = "\n".join(lines)
    assert "0 0 * * 0" in combined
    assert "weekly" in combined


def test_import_from_file(tmp_fav, tmp_path):
    import_file = tmp_path / "import.json"
    records = [{"name": "hourly", "expression": "0 * * * *"}]
    import_file.write_text(json.dumps(records))
    lines = []
    cmd_import_favorites(args(file=str(import_file), fav_path=str(tmp_fav)), out=lines.append)
    assert any("hourly" in l for l in lines)
    assert any("imported" in l.lower() for l in lines)


def test_import_skips_invalid_expression(tmp_fav, tmp_path):
    import_file = tmp_path / "import.json"
    records = [{"name": "bad", "expression": "99 99 99 99 99"}]
    import_file.write_text(json.dumps(records))
    lines = []
    cmd_import_favorites(args(file=str(import_file), fav_path=str(tmp_fav)), out=lines.append)
    assert any("Skipping" in l for l in lines)


def test_import_bad_file(tmp_fav, tmp_path):
    lines = []
    cmd_import_favorites(args(file="/nonexistent/file.json", fav_path=str(tmp_fav)), out=lines.append)
    assert any("Error" in l for l in lines)


def test_import_missing_fields(tmp_fav, tmp_path):
    import_file = tmp_path / "import.json"
    records = [{"name": "no_expr"}]
    import_file.write_text(json.dumps(records))
    lines = []
    cmd_import_favorites(args(file=str(import_file), fav_path=str(tmp_fav)), out=lines.append)
    assert any("Skipping invalid record" in l for l in lines)
