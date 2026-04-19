import pytest
from pathlib import Path
from crontab_buddy.label import (
    add_label, remove_label, get_labels, find_by_label, list_all_labels
)


@pytest.fixture
def tmp_label(tmp_path):
    return tmp_path / "labels.json"


def test_add_and_get_label(tmp_label):
    add_label("* * * * *", "frequent", path=tmp_label)
    assert "frequent" in get_labels("* * * * *", path=tmp_label)


def test_add_duplicate_returns_false(tmp_label):
    add_label("* * * * *", "frequent", path=tmp_label)
    result = add_label("* * * * *", "frequent", path=tmp_label)
    assert result is False


def test_add_multiple_labels(tmp_label):
    add_label("0 * * * *", "hourly", path=tmp_label)
    add_label("0 * * * *", "important", path=tmp_label)
    labels = get_labels("0 * * * *", path=tmp_label)
    assert "hourly" in labels
    assert "important" in labels


def test_remove_label(tmp_label):
    add_label("0 0 * * *", "daily", path=tmp_label)
    result = remove_label("0 0 * * *", "daily", path=tmp_label)
    assert result is True
    assert get_labels("0 0 * * *", path=tmp_label) == []


def test_remove_missing_label_returns_false(tmp_label):
    result = remove_label("0 0 * * *", "nonexistent", path=tmp_label)
    assert result is False


def test_find_by_label(tmp_label):
    add_label("* * * * *", "frequent", path=tmp_label)
    add_label("0 * * * *", "frequent", path=tmp_label)
    add_label("0 0 * * *", "daily", path=tmp_label)
    results = find_by_label("frequent", path=tmp_label)
    assert "* * * * *" in results
    assert "0 * * * *" in results
    assert "0 0 * * *" not in results


def test_find_by_label_no_match(tmp_label):
    assert find_by_label("ghost", path=tmp_label) == []


def test_list_all_labels(tmp_label):
    add_label("* * * * *", "a", path=tmp_label)
    add_label("0 * * * *", "b", path=tmp_label)
    data = list_all_labels(path=tmp_label)
    assert "* * * * *" in data
    assert "0 * * * *" in data


def test_remove_last_label_removes_key(tmp_label):
    add_label("5 4 * * *", "solo", path=tmp_label)
    remove_label("5 4 * * *", "solo", path=tmp_label)
    data = list_all_labels(path=tmp_label)
    assert "5 4 * * *" not in data
