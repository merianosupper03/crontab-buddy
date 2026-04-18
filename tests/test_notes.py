import pytest
import os
from crontab_buddy.notes import set_note, get_note, delete_note, list_notes
from crontab_buddy.notes_cli import cmd_note_set, cmd_note_get, cmd_note_delete, cmd_note_list


@pytest.fixture
def tmp_notes(tmp_path):
    return str(tmp_path / "notes.json")


def test_set_and_get_note(tmp_notes):
    set_note("0 * * * *", "every hour", path=tmp_notes)
    assert get_note("0 * * * *", path=tmp_notes) == "every hour"


def test_get_missing_note_returns_none(tmp_notes):
    assert get_note("* * * * *", path=tmp_notes) is None


def test_overwrite_note(tmp_notes):
    set_note("0 0 * * *", "daily", path=tmp_notes)
    set_note("0 0 * * *", "midnight daily", path=tmp_notes)
    assert get_note("0 0 * * *", path=tmp_notes) == "midnight daily"


def test_delete_existing_note(tmp_notes):
    set_note("0 12 * * *", "noon", path=tmp_notes)
    result = delete_note("0 12 * * *", path=tmp_notes)
    assert result is True
    assert get_note("0 12 * * *", path=tmp_notes) is None


def test_delete_missing_note_returns_false(tmp_notes):
    assert delete_note("5 4 * * *", path=tmp_notes) is False


def test_list_notes(tmp_notes):
    set_note("0 * * * *", "hourly", path=tmp_notes)
    set_note("0 0 * * *", "daily", path=tmp_notes)
    notes = list_notes(path=tmp_notes)
    assert notes["0 * * * *"] == "hourly"
    assert notes["0 0 * * *"] == "daily"


def test_list_empty_notes(tmp_notes):
    assert list_notes(path=tmp_notes) == {}


def test_cmd_note_set_prints(tmp_notes, capsys):
    cmd_note_set("* * * * *", "every minute", path=tmp_notes)
    out = capsys.readouterr().out
    assert "saved" in out


def test_cmd_note_get_found(tmp_notes, capsys):
    set_note("0 6 * * *", "morning", path=tmp_notes)
    cmd_note_get("0 6 * * *", path=tmp_notes)
    out = capsys.readouterr().out
    assert "morning" in out


def test_cmd_note_get_missing(tmp_notes, capsys):
    cmd_note_get("1 2 3 4 5", path=tmp_notes)
    out = capsys.readouterr().out
    assert "No note" in out


def test_cmd_note_delete_success(tmp_notes, capsys):
    set_note("0 0 1 * *", "monthly", path=tmp_notes)
    cmd_note_delete("0 0 1 * *", path=tmp_notes)
    out = capsys.readouterr().out
    assert "deleted" in out


def test_cmd_note_list_empty(tmp_notes, capsys):
    cmd_note_list(path=tmp_notes)
    out = capsys.readouterr().out
    assert "No notes" in out
