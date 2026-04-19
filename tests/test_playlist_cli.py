import pytest
from pathlib import Path
from crontab_buddy.playlist_cli import (
    cmd_playlist_create, cmd_playlist_add, cmd_playlist_remove,
    cmd_playlist_list, cmd_playlist_delete, cmd_playlist_all,
)
from crontab_buddy.playlist import create_playlist, add_to_playlist


class Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


@pytest.fixture
def tp(tmp_path):
    return tmp_path / "playlists.json"


def test_cmd_create_prints(tp):
    out = []
    cmd_playlist_create(Args(name="work", path=tp), print_fn=out.append)
    assert "created" in out[0]


def test_cmd_create_duplicate_message(tp):
    create_playlist("work", path=tp)
    out = []
    cmd_playlist_create(Args(name="work", path=tp), print_fn=out.append)
    assert "already exists" in out[0]


def test_cmd_add_prints_added(tp):
    create_playlist("daily", path=tp)
    out = []
    cmd_playlist_add(Args(name="daily", expression="0 9 * * *", path=tp), print_fn=out.append)
    assert "Added" in out[0]


def test_cmd_add_missing_playlist(tp):
    out = []
    cmd_playlist_add(Args(name="ghost", expression="0 9 * * *", path=tp), print_fn=out.append)
    assert "not found" in out[0]


def test_cmd_remove_success(tp):
    create_playlist("daily", path=tp)
    add_to_playlist("daily", "0 9 * * *", path=tp)
    out = []
    cmd_playlist_remove(Args(name="daily", expression="0 9 * * *", path=tp), print_fn=out.append)
    assert "Removed" in out[0]


def test_cmd_list_shows_expressions(tp):
    create_playlist("daily", path=tp)
    add_to_playlist("daily", "0 9 * * *", path=tp)
    out = []
    cmd_playlist_list(Args(name="daily", path=tp), print_fn=out.append)
    assert any("0 9 * * *" in line for line in out)


def test_cmd_list_empty(tp):
    create_playlist("empty", path=tp)
    out = []
    cmd_playlist_list(Args(name="empty", path=tp), print_fn=out.append)
    assert "empty" in out[0].lower()


def test_cmd_delete_success(tp):
    create_playlist("temp", path=tp)
    out = []
    cmd_playlist_delete(Args(name="temp", path=tp), print_fn=out.append)
    assert "deleted" in out[0].lower()


def test_cmd_all_lists_names(tp):
    create_playlist("a", path=tp)
    create_playlist("b", path=tp)
    out = []
    cmd_playlist_all(Args(path=tp), print_fn=out.append)
    assert "a" in out and "b" in out
