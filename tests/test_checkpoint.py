"""Tests for crontab_buddy.checkpoint."""

import pytest
from crontab_buddy.checkpoint import (
    save_checkpoint,
    get_checkpoint,
    delete_checkpoint,
    list_checkpoints,
    search_checkpoints,
)


@pytest.fixture
def tmp_cp(tmp_path):
    return str(tmp_path / "checkpoints.json")


def test_save_and_get(tmp_cp):
    save_checkpoint("daily", "0 9 * * *", path=tmp_cp)
    cp = get_checkpoint("daily", path=tmp_cp)
    assert cp is not None
    assert cp["expression"] == "0 9 * * *"


def test_get_missing_returns_none(tmp_cp):
    assert get_checkpoint("missing", path=tmp_cp) is None


def test_name_is_case_insensitive(tmp_cp):
    save_checkpoint("WEEKLY", "0 0 * * 0", path=tmp_cp)
    assert get_checkpoint("weekly", path=tmp_cp) is not None
    assert get_checkpoint("WEEKLY", path=tmp_cp) is not None


def test_overwrite_checkpoint(tmp_cp):
    save_checkpoint("job", "0 1 * * *", path=tmp_cp)
    save_checkpoint("job", "0 2 * * *", path=tmp_cp)
    cp = get_checkpoint("job", path=tmp_cp)
    assert cp["expression"] == "0 2 * * *"


def test_delete_existing(tmp_cp):
    save_checkpoint("temp", "* * * * *", path=tmp_cp)
    assert delete_checkpoint("temp", path=tmp_cp) is True
    assert get_checkpoint("temp", path=tmp_cp) is None


def test_delete_missing_returns_false(tmp_cp):
    assert delete_checkpoint("ghost", path=tmp_cp) is False


def test_list_checkpoints_empty(tmp_cp):
    assert list_checkpoints(path=tmp_cp) == []


def test_list_checkpoints_multiple(tmp_cp):
    save_checkpoint("a", "0 1 * * *", path=tmp_cp)
    save_checkpoint("b", "0 2 * * *", path=tmp_cp)
    result = list_checkpoints(path=tmp_cp)
    assert len(result) == 2
    names = [r["name"] for r in result]
    assert "a" in names and "b" in names


def test_checkpoint_has_saved_at(tmp_cp):
    save_checkpoint("ts", "5 4 * * *", path=tmp_cp)
    cp = get_checkpoint("ts", path=tmp_cp)
    assert "saved_at" in cp


def test_checkpoint_with_note(tmp_cp):
    save_checkpoint("noted", "0 6 * * 1", note="weekly Monday", path=tmp_cp)
    cp = get_checkpoint("noted", path=tmp_cp)
    assert cp["note"] == "weekly Monday"


def test_search_by_expression(tmp_cp):
    save_checkpoint("midnight", "0 0 * * *", path=tmp_cp)
    save_checkpoint("noon", "0 12 * * *", path=tmp_cp)
    results = search_checkpoints("0 0", path=tmp_cp)
    assert len(results) == 1
    assert results[0]["name"] == "midnight"


def test_search_by_name(tmp_cp):
    save_checkpoint("deploy-prod", "30 2 * * 0", path=tmp_cp)
    results = search_checkpoints("deploy", path=tmp_cp)
    assert any(r["name"] == "deploy-prod" for r in results)


def test_search_by_note(tmp_cp):
    save_checkpoint("backup", "0 3 * * *", note="nightly backup job", path=tmp_cp)
    results = search_checkpoints("nightly", path=tmp_cp)
    assert len(results) == 1


def test_search_no_match(tmp_cp):
    save_checkpoint("x", "* * * * *", path=tmp_cp)
    assert search_checkpoints("zzznomatch", path=tmp_cp) == []
