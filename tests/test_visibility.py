"""Tests for crontab_buddy/visibility.py"""

import json
import pytest
from unittest.mock import patch

from crontab_buddy import visibility as vis


@pytest.fixture
def tmp_vis(tmp_path, monkeypatch):
    path = str(tmp_path / "visibility.json")
    monkeypatch.setattr(vis, "_FILE", path)
    return path


def test_set_and_get(tmp_vis):
    vis.set_visibility("0 * * * *", "public")
    result = vis.get_visibility("0 * * * *")
    assert result is not None
    assert result["level"] == "public"


def test_get_missing_returns_none(tmp_vis):
    assert vis.get_visibility("* * * * *") is None


def test_set_team_visibility(tmp_vis):
    vis.set_visibility("0 9 * * 1", "team", team="devops")
    result = vis.get_visibility("0 9 * * 1")
    assert result["level"] == "team"
    assert result["team"] == "devops"


def test_team_without_name_raises(tmp_vis):
    with pytest.raises(ValueError, match="team name"):
        vis.set_visibility("0 9 * * 1", "team")


def test_invalid_level_raises(tmp_vis):
    with pytest.raises(ValueError, match="Invalid visibility level"):
        vis.set_visibility("0 * * * *", "hidden")


def test_overwrite_visibility(tmp_vis):
    vis.set_visibility("0 * * * *", "public")
    vis.set_visibility("0 * * * *", "private")
    result = vis.get_visibility("0 * * * *")
    assert result["level"] == "private"


def test_delete_existing(tmp_vis):
    vis.set_visibility("0 * * * *", "public")
    assert vis.delete_visibility("0 * * * *") is True
    assert vis.get_visibility("0 * * * *") is None


def test_delete_missing_returns_false(tmp_vis):
    assert vis.delete_visibility("* * * * *") is False


def test_list_visibility_empty(tmp_vis):
    assert vis.list_visibility() == []


def test_list_visibility_multiple(tmp_vis):
    vis.set_visibility("0 * * * *", "public")
    vis.set_visibility("0 9 * * 1", "private")
    entries = vis.list_visibility()
    assert len(entries) == 2
    exprs = [e["expression"] for e in entries]
    assert "0 * * * *" in exprs
    assert "0 9 * * 1" in exprs


def test_filter_by_level(tmp_vis):
    vis.set_visibility("0 * * * *", "public")
    vis.set_visibility("0 9 * * 1", "private")
    vis.set_visibility("*/5 * * * *", "public")
    public = vis.filter_by_level("public")
    assert "0 * * * *" in public
    assert "*/5 * * * *" in public
    assert "0 9 * * 1" not in public


def test_all_valid_levels_accepted(tmp_vis):
    for i, level in enumerate(vis.VALID_LEVELS):
        expr = f"{i} * * * *"
        team = "eng" if level == "team" else None
        vis.set_visibility(expr, level, team=team)
        result = vis.get_visibility(expr)
        assert result["level"] == level
