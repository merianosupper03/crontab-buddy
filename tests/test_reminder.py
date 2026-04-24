import pytest
from pathlib import Path
from crontab_buddy.reminder import set_reminder, get_reminder, delete_reminder, list_reminders


@pytest.fixture
def tmp_reminder(tmp_path):
    return tmp_path / "reminders.json"


def test_set_and_get(tmp_reminder):
    set_reminder("0 9 * * 1", "Weekly Monday standup", path=tmp_reminder)
    assert get_reminder("0 9 * * 1", path=tmp_reminder) == "Weekly Monday standup"


def test_get_missing_returns_none(tmp_reminder):
    assert get_reminder("* * * * *", path=tmp_reminder) is None


def test_overwrite_reminder(tmp_reminder):
    set_reminder("0 0 * * *", "Old note", path=tmp_reminder)
    set_reminder("0 0 * * *", "New note", path=tmp_reminder)
    assert get_reminder("0 0 * * *", path=tmp_reminder) == "New note"


def test_delete_existing(tmp_reminder):
    set_reminder("5 4 * * *", "Backup job", path=tmp_reminder)
    result = delete_reminder("5 4 * * *", path=tmp_reminder)
    assert result is True
    assert get_reminder("5 4 * * *", path=tmp_reminder) is None


def test_delete_missing_returns_false(tmp_reminder):
    assert delete_reminder("1 2 3 4 5", path=tmp_reminder) is False


def test_list_reminders_empty(tmp_reminder):
    assert list_reminders(path=tmp_reminder) == {}


def test_list_reminders_multiple(tmp_reminder):
    set_reminder("0 6 * * *", "Morning job", path=tmp_reminder)
    set_reminder("0 18 * * *", "Evening job", path=tmp_reminder)
    result = list_reminders(path=tmp_reminder)
    assert len(result) == 2
    assert result["0 6 * * *"] == "Morning job"
    assert result["0 18 * * *"] == "Evening job"


def test_message_is_stripped(tmp_reminder):
    set_reminder("* * * * *", "  trimmed  ", path=tmp_reminder)
    assert get_reminder("* * * * *", path=tmp_reminder) == "trimmed"


def test_set_reminder_raises_on_empty_message(tmp_reminder):
    """set_reminder should reject blank or whitespace-only messages."""
    with pytest.raises(ValueError):
        set_reminder("0 9 * * 1", "", path=tmp_reminder)

    with pytest.raises(ValueError):
        set_reminder("0 9 * * 1", "   ", path=tmp_reminder)
