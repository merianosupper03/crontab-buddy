import pytest
from crontab_buddy.schedule_name_cli import (
    cmd_schedule_save, cmd_schedule_get, cmd_schedule_delete, cmd_schedule_list
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    return tmp_path / "sched.json"


def test_cmd_save_prints(tp, capsys):
    args = Args(name="daily", expression="0 9 * * *", description="")
    cmd_schedule_save(args, path=tp)
    out = capsys.readouterr().out
    assert "daily" in out
    assert "0 9 * * *" in out


def test_cmd_get_existing(tp, capsys):
    args = Args(name="daily", expression="0 9 * * *", description="morning")
    cmd_schedule_save(args, path=tp)
    cmd_schedule_get(Args(name="daily"), path=tp)
    out = capsys.readouterr().out
    assert "0 9 * * *" in out
    assert "morning" in out


def test_cmd_get_missing(tp, capsys):
    cmd_schedule_get(Args(name="ghost"), path=tp)
    out = capsys.readouterr().out
    assert "No schedule" in out


def test_cmd_delete_success(tp, capsys):
    args = Args(name="x", expression="* * * * *", description="")
    cmd_schedule_save(args, path=tp)
    cmd_schedule_delete(Args(name="x"), path=tp)
    out = capsys.readouterr().out
    assert "Deleted" in out


def test_cmd_delete_missing(tp, capsys):
    cmd_schedule_delete(Args(name="missing"), path=tp)
    out = capsys.readouterr().out
    assert "No schedule" in out


def test_cmd_list_empty(tp, capsys):
    cmd_schedule_list(Args(), path=tp)
    out = capsys.readouterr().out
    assert "No named" in out


def test_cmd_list_shows_entries(tp, capsys):
    cmd_schedule_save(Args(name="weekly", expression="0 8 * * 1", description=""), path=tp)
    cmd_schedule_list(Args(), path=tp)
    out = capsys.readouterr().out
    assert "weekly" in out
    assert "0 8 * * 1" in out
