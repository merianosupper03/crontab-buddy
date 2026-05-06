import pytest
from crontab_buddy.symmetry import check_symmetry, batch_symmetry, SymmetryResult


def test_identical_expressions_are_symmetric():
    result = check_symmetry("0 9 * * 1", "0 9 * * 1")
    assert result.symmetric is True
    assert "all fields match" in result.reason


def test_different_minute_not_symmetric():
    result = check_symmetry("0 9 * * 1", "5 9 * * 1")
    assert result.symmetric is False
    assert "minute" in result.reason


def test_different_hour_not_symmetric():
    result = check_symmetry("0 8 * * *", "0 10 * * *")
    assert result.symmetric is False
    assert "hour" in result.reason


def test_multiple_field_differences():
    result = check_symmetry("0 8 1 * *", "30 12 * * 5")
    assert result.symmetric is False
    for field in ["minute", "hour", "dom", "dow"]:
        assert field in result.reason


def test_wildcard_vs_explicit_not_symmetric():
    result = check_symmetry("* * * * *", "0 0 * * *")
    assert result.symmetric is False


def test_invalid_expr_a_returns_false():
    result = check_symmetry("bad expr", "0 9 * * *")
    assert result.symmetric is False
    assert "invalid" in result.reason


def test_invalid_expr_b_returns_false():
    result = check_symmetry("0 9 * * *", "not valid")
    assert result.symmetric is False
    assert "invalid" in result.reason


def test_bool_true_for_symmetric():
    result = check_symmetry("*/5 * * * *", "*/5 * * * *")
    assert bool(result) is True


def test_bool_false_for_not_symmetric():
    result = check_symmetry("*/5 * * * *", "*/10 * * * *")
    assert bool(result) is False


def test_str_contains_symmetric_label():
    result = check_symmetry("0 0 * * *", "0 0 * * *")
    assert "symmetric" in str(result)


def test_str_contains_not_symmetric_label():
    result = check_symmetry("0 0 * * *", "0 1 * * *")
    assert "not symmetric" in str(result)


def test_batch_symmetry_returns_pairs():
    exprs = ["0 9 * * *", "0 9 * * *", "0 10 * * *"]
    results = batch_symmetry(exprs)
    assert len(results) == 2


def test_batch_symmetry_first_pair_symmetric():
    exprs = ["0 9 * * *", "0 9 * * *", "0 10 * * *"]
    results = batch_symmetry(exprs)
    assert results[0].symmetric is True


def test_batch_symmetry_second_pair_not_symmetric():
    exprs = ["0 9 * * *", "0 9 * * *", "0 10 * * *"]
    results = batch_symmetry(exprs)
    assert results[1].symmetric is False


def test_batch_symmetry_empty_list():
    assert batch_symmetry([]) == []


def test_batch_symmetry_single_item():
    assert batch_symmetry(["0 9 * * *"]) == []
