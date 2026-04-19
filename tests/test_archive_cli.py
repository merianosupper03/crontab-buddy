import pytest
from crontab_buddy.archive_cli import (
    cmd_archive_add, cmd_archive_delete, cmd_archive_list,
    cmd_archive_search, cmd_archive_clear
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "archive.json")


def test_cmd_archive_add_prints(tp, capsys):
    args = Args(expression="0 9 * * 1", reason="", path=tp)
    cmd_archive_add(args)
    out = capsys.readouterr().out
    assert "0 9 * * 1" in out
    assert "Archived" in out


def test_cmd_archive_add_with_reason(tp, capsys):
    args = Args(expression="0 9 * * 1", reason="replaced", path=tp)
    cmd_archive_add(args)
    out = capsys.readouterr().out
    assert "replaced" in out


def test_cmd_archive_list_empty(tp, capsys):
    args = Args(path=tp)
    cmd_archive_list(args)
    assert "empty" in capsys.readouterr().out


def test_cmd_archive_list_shows_entries(tp, capsys):
    cmd_archive_add(Args(expression="*/5 * * * *", reason="", path=tp))
    capsys.readouterr()
    cmd_archive_list(Args(path=tp))
    assert "*/5 * * * *" in capsys.readouterr().out


def test_cmd_archive_delete_success(tp, capsys):
    cmd_archive_add(Args(expression="0 0 * * *", reason="", path=tp))
    capsys.readouterr()
    cmd_archive_delete(Args(expression="0 0 * * *", path=tp))
    assert "Removed" in capsys.readouterr().out


def test_cmd_archive_delete_missing(tp, capsys):
    cmd_archive_delete(Args(expression="0 0 * * *", path=tp))
    assert "not found" in capsys.readouterr().out


def test_cmd_archive_search_match(tp, capsys):
    cmd_archive_add(Args(expression="0 12 * * *", reason="noon job", path=tp))
    capsys.readouterr()
    cmd_archive_search(Args(keyword="noon", path=tp))
    assert "0 12 * * *" in capsys.readouterr().out


def test_cmd_archive_search_no_match(tp, capsys):
    cmd_archive_search(Args(keyword="xyz", path=tp))
    assert "No matching" in capsys.readouterr().out


def test_cmd_archive_clear(tp, capsys):
    cmd_archive_add(Args(expression="* * * * *", reason="", path=tp))
    capsys.readouterr()
    cmd_archive_clear(Args(path=tp))
    assert "cleared" in capsys.readouterr().out
