import pytest
from pathlib import Path
from crontab_buddy.playlist import (
    create_playlist, add_to_playlist, remove_from_playlist,
    get_playlist, delete_playlist, list_playlists,
)


@pytest.fixture
def tmp_pl(tmp_path):
    return tmp_path / "playlists.json"


def test_create_playlist(tmp_pl):
    assert create_playlist("work", path=tmp_pl) is True
    assert "work" in list_playlists(path=tmp_pl)


def test_create_duplicate_returns_false(tmp_pl):
    create_playlist("work", path=tmp_pl)
    assert create_playlist("work", path=tmp_pl) is False


def test_create_is_case_insensitive(tmp_pl):
    create_playlist("Work", path=tmp_pl)
    assert create_playlist("work", path=tmp_pl) is False


def test_add_to_playlist(tmp_pl):
    create_playlist("daily", path=tmp_pl)
    assert add_to_playlist("daily", "0 9 * * *", path=tmp_pl) is True
    assert "0 9 * * *" in get_playlist("daily", path=tmp_pl)


def test_add_to_missing_playlist_returns_false(tmp_pl):
    assert add_to_playlist("ghost", "0 9 * * *", path=tmp_pl) is False


def test_no_duplicate_expressions(tmp_pl):
    create_playlist("daily", path=tmp_pl)
    add_to_playlist("daily", "0 9 * * *", path=tmp_pl)
    add_to_playlist("daily", "0 9 * * *", path=tmp_pl)
    assert len(get_playlist("daily", path=tmp_pl)) == 1


def test_add_multiple_expressions(tmp_pl):
    create_playlist("multi", path=tmp_pl)
    add_to_playlist("multi", "0 9 * * *", path=tmp_pl)
    add_to_playlist("multi", "30 18 * * *", path=tmp_pl)
    assert len(get_playlist("multi", path=tmp_pl)) == 2


def test_remove_expression(tmp_pl):
    create_playlist("daily", path=tmp_pl)
    add_to_playlist("daily", "0 9 * * *", path=tmp_pl)
    assert remove_from_playlist("daily", "0 9 * * *", path=tmp_pl) is True
    assert get_playlist("daily", path=tmp_pl) == []


def test_remove_missing_expression_returns_false(tmp_pl):
    create_playlist("daily", path=tmp_pl)
    assert remove_from_playlist("daily", "0 9 * * *", path=tmp_pl) is False


def test_get_missing_playlist_returns_none(tmp_pl):
    assert get_playlist("nope", path=tmp_pl) is None


def test_delete_playlist(tmp_pl):
    create_playlist("temp", path=tmp_pl)
    assert delete_playlist("temp", path=tmp_pl) is True
    assert get_playlist("temp", path=tmp_pl) is None


def test_delete_missing_returns_false(tmp_pl):
    assert delete_playlist("ghost", path=tmp_pl) is False


def test_list_playlists_empty(tmp_pl):
    assert list_playlists(path=tmp_pl) == []
