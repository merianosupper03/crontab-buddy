import pytest
from pathlib import Path
from crontab_buddy.schedule_name import save_schedule, get_schedule, delete_schedule, list_schedules


@pytest.fixture
def tmp_sched(tmp_path):
    return tmp_path / "schedule_names.json"


def test_save_and_get(tmp_sched):
    save_schedule("daily", "0 9 * * *", path=tmp_sched)
    result = get_schedule("daily", path=tmp_sched)
    assert result is not None
    assert result["expression"] == "0 9 * * *"


def test_get_missing_returns_none(tmp_sched):
    assert get_schedule("nope", path=tmp_sched) is None


def test_name_is_case_insensitive(tmp_sched):
    save_schedule("Weekly", "0 8 * * 1", path=tmp_sched)
    assert get_schedule("weekly", path=tmp_sched) is not None
    assert get_schedule("WEEKLY", path=tmp_sched) is not None


def test_overwrite_schedule(tmp_sched):
    save_schedule("job", "0 1 * * *", path=tmp_sched)
    save_schedule("job", "0 2 * * *", path=tmp_sched)
    result = get_schedule("job", path=tmp_sched)
    assert result["expression"] == "0 2 * * *"


def test_delete_existing(tmp_sched):
    save_schedule("temp", "* * * * *", path=tmp_sched)
    assert delete_schedule("temp", path=tmp_sched) is True
    assert get_schedule("temp", path=tmp_sched) is None


def test_delete_missing_returns_false(tmp_sched):
    assert delete_schedule("ghost", path=tmp_sched) is False


def test_list_schedules(tmp_sched):
    save_schedule("a", "0 1 * * *", path=tmp_sched)
    save_schedule("b", "0 2 * * *", path=tmp_sched)
    schedules = list_schedules(path=tmp_sched)
    assert "a" in schedules
    assert "b" in schedules


def test_list_empty(tmp_sched):
    assert list_schedules(path=tmp_sched) == {}


def test_save_with_description(tmp_sched):
    save_schedule("nightly", "0 0 * * *", description="Runs at midnight", path=tmp_sched)
    result = get_schedule("nightly", path=tmp_sched)
    assert result["description"] == "Runs at midnight"
