import pytest
from types import SimpleNamespace
from crontab_buddy.collections_cli import (
    cmd_collection_add, cmd_collection_remove,
    cmd_collection_list, cmd_collection_delete, cmd_collection_all
)


@pytest.fixture
def tp(tmp_path):
    return tmp_path / "collections.json"


def args(**kwargs):
    return SimpleNamespace(**kwargs)


def test_cmd_add_prints_added(tp, capsys):
    cmd_collection_add(args(name="work", expression="0 9 * * 1-5"), path=tp)
    out = capsys.readouterr().out
    assert "Added" in out


def test_cmd_add_duplicate_message(tp, capsys):
    cmd_collection_add(args(name="work", expression="0 9 * * 1-5"), path=tp)
    cmd_collection_add(args(name="work", expression="0 9 * * 1-5"), path=tp)
    out = capsys.readouterr().out
    assert "already" in out


def test_cmd_remove_success(tp, capsys):
    cmd_collection_add(args(name="work", expression="0 9 * * 1-5"), path=tp)
    capsys.readouterr()
    cmd_collection_remove(args(name="work", expression="0 9 * * 1-5"), path=tp)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_remove_missing(tp, capsys):
    cmd_collection_remove(args(name="work", expression="0 9 * * 1-5"), path=tp)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_list_shows_expressions(tp, capsys):
    cmd_collection_add(args(name="daily", expression="0 0 * * *"), path=tp)
    capsys.readouterr()
    cmd_collection_list(args(name="daily"), path=tp)
    out = capsys.readouterr().out
    assert "0 0 * * *" in out


def test_cmd_list_missing_collection(tp, capsys):
    cmd_collection_list(args(name="ghost"), path=tp)
    out = capsys.readouterr().out
    assert "does not exist" in out


def test_cmd_delete_success(tp, capsys):
    cmd_collection_add(args(name="temp", expression="* * * * *"), path=tp)
    capsys.readouterr()
    cmd_collection_delete(args(name="temp"), path=tp)
    out = capsys.readouterr().out
    assert "Deleted" in out


def test_cmd_all_lists_names(tp, capsys):
    cmd_collection_add(args(name="a", expression="* * * * *"), path=tp)
    cmd_collection_add(args(name="b", expression="0 0 * * *"), path=tp)
    capsys.readouterr()
    cmd_collection_all(args(), path=tp)
    out = capsys.readouterr().out
    assert "[a]" in out and "[b]" in out
