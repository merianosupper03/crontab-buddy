"""Tests for crontab_buddy.concurrency."""
import pytest

from crontab_buddy.concurrency import (
    VALID_POLICIES,
    delete_concurrency,
    get_concurrency,
    list_concurrency,
    set_concurrency,
)


@pytest.fixture(autouse=True)
def tmp_concurrency(tmp_path, monkeypatch):
    data_file = tmp_path / "concurrency.json"
    import crontab_buddy.concurrency as mod
    monkeypatch.setattr(mod, "_DATA_FILE", data_file)
    yield data_file


def test_set_and_get():
    set_concurrency("* * * * *", "skip")
    entry = get_concurrency("* * * * *")
    assert entry is not None
    assert entry["policy"] == "skip"
    assert entry["max_instances"] == 1


def test_get_missing_returns_none():
    assert get_concurrency("0 * * * *") is None


def test_overwrite_concurrency():
    set_concurrency("0 0 * * *", "allow", 1)
    set_concurrency("0 0 * * *", "queue", 3)
    entry = get_concurrency("0 0 * * *")
    assert entry["policy"] == "queue"
    assert entry["max_instances"] == 3


def test_invalid_policy_raises():
    with pytest.raises(ValueError, match="Invalid policy"):
        set_concurrency("* * * * *", "explode")


def test_invalid_max_instances_raises():
    with pytest.raises(ValueError, match="max_instances"):
        set_concurrency("* * * * *", "allow", 0)


def test_all_valid_policies_accepted():
    for i, policy in enumerate(VALID_POLICIES):
        expr = f"{i} * * * *"
        set_concurrency(expr, policy)
        assert get_concurrency(expr)["policy"] == policy


def test_delete_existing():
    set_concurrency("5 * * * *", "kill")
    assert delete_concurrency("5 * * * *") is True
    assert get_concurrency("5 * * * *") is None


def test_delete_missing_returns_false():
    assert delete_concurrency("9 9 9 9 *") is False


def test_list_concurrency_empty():
    assert list_concurrency() == {}


def test_list_concurrency_multiple():
    set_concurrency("* * * * *", "skip", 1)
    set_concurrency("0 0 * * *", "queue", 2)
    result = list_concurrency()
    assert len(result) == 2
    assert result["* * * * *"]["policy"] == "skip"
    assert result["0 0 * * *"]["max_instances"] == 2


def test_max_instances_stored_correctly():
    set_concurrency("30 6 * * 1", "allow", 5)
    entry = get_concurrency("30 6 * * 1")
    assert entry["max_instances"] == 5
