import pytest
import os
from crontab_buddy import goal as _goal


@pytest.fixture
def tmp_goal(tmp_path):
    return str(tmp_path / "goals.json")


def test_set_and_get_goal(tmp_goal):
    _goal.set_goal("0 9 * * 1", 10, path=tmp_goal)
    g = _goal.get_goal("0 9 * * 1", path=tmp_goal)
    assert g is not None
    assert g["target"] == 10
    assert g["count"] == 0


def test_get_missing_returns_none(tmp_goal):
    assert _goal.get_goal("* * * * *", path=tmp_goal) is None


def test_invalid_target_raises(tmp_goal):
    with pytest.raises(ValueError):
        _goal.set_goal("* * * * *", 0, path=tmp_goal)


def test_record_run_increments(tmp_goal):
    _goal.set_goal("0 0 * * *", 5, path=tmp_goal)
    c1 = _goal.record_run("0 0 * * *", path=tmp_goal)
    c2 = _goal.record_run("0 0 * * *", path=tmp_goal)
    assert c1 == 1
    assert c2 == 2


def test_record_run_without_goal(tmp_goal):
    count = _goal.record_run("5 4 * * *", path=tmp_goal)
    assert count == 1


def test_progress_ratio(tmp_goal):
    _goal.set_goal("0 12 * * *", 4, path=tmp_goal)
    _goal.record_run("0 12 * * *", path=tmp_goal)
    _goal.record_run("0 12 * * *", path=tmp_goal)
    p = _goal.progress("0 12 * * *", path=tmp_goal)
    assert p == pytest.approx(0.5)


def test_progress_no_goal_returns_none(tmp_goal):
    assert _goal.progress("* * * * *", path=tmp_goal) is None


def test_delete_existing(tmp_goal):
    _goal.set_goal("0 6 * * *", 3, path=tmp_goal)
    result = _goal.delete_goal("0 6 * * *", path=tmp_goal)
    assert result is True
    assert _goal.get_goal("0 6 * * *", path=tmp_goal) is None


def test_delete_missing_returns_false(tmp_goal):
    assert _goal.delete_goal("1 1 1 1 1", path=tmp_goal) is False


def test_list_goals(tmp_goal):
    _goal.set_goal("0 9 * * 1", 5, path=tmp_goal)
    _goal.set_goal("0 17 * * 5", 3, path=tmp_goal)
    goals = _goal.list_goals(path=tmp_goal)
    exprs = [g["expression"] for g in goals]
    assert "0 9 * * 1" in exprs
    assert "0 17 * * 5" in exprs


def test_overwrite_preserves_count(tmp_goal):
    _goal.set_goal("0 8 * * *", 10, path=tmp_goal)
    _goal.record_run("0 8 * * *", path=tmp_goal)
    _goal.set_goal("0 8 * * *", 20, path=tmp_goal)
    g = _goal.get_goal("0 8 * * *", path=tmp_goal)
    assert g["target"] == 20
    assert g["count"] == 1
