import pytest
from crontab_buddy.chain import build_chain, format_chain, chain_valid


SIMPLE = [{"expression": "0 9 * * 1", "label": "weekly-report"},
          {"expression": "30 17 * * 5", "label": "friday-cleanup"}]


def test_build_chain_valid_entries():
    result = build_chain(SIMPLE)
    assert len(result) == 2
    assert all(r["valid"] for r in result)


def test_build_chain_preserves_labels():
    result = build_chain(SIMPLE)
    assert result[0]["label"] == "weekly-report"
    assert result[1]["label"] == "friday-cleanup"


def test_build_chain_has_description():
    result = build_chain(SIMPLE)
    for r in result:
        assert r["description"]
        assert r["description"] != "(invalid)"


def test_build_chain_invalid_expression():
    entries = [{"expression": "99 99 * * *", "label": "bad"}]
    result = build_chain(entries)
    assert result[0]["valid"] is False
    assert result[0]["error"] is not None
    assert result[0]["description"] == "(invalid)"


def test_build_chain_auto_label():
    entries = [{"expression": "* * * * *"}]
    result = build_chain(entries)
    assert result[0]["label"] == "step-1"


def test_build_chain_mixed_validity():
    entries = [
        {"expression": "0 6 * * *", "label": "good"},
        {"expression": "bad expr", "label": "bad"},
    ]
    result = build_chain(entries)
    assert result[0]["valid"] is True
    assert result[1]["valid"] is False


def test_chain_valid_all_good():
    result = build_chain(SIMPLE)
    assert chain_valid(result) is True


def test_chain_valid_with_bad_entry():
    entries = [
        {"expression": "0 6 * * *"},
        {"expression": "nope"},
    ]
    result = build_chain(entries)
    assert chain_valid(result) is False


def test_format_chain_contains_labels():
    result = build_chain(SIMPLE)
    output = format_chain(result)
    assert "weekly-report" in output
    assert "friday-cleanup" in output


def test_format_chain_shows_ok():
    result = build_chain(SIMPLE)
    output = format_chain(result)
    assert "[OK]" in output


def test_format_chain_shows_fail():
    entries = [{"expression": "bad", "label": "broken"}]
    result = build_chain(entries)
    output = format_chain(result)
    assert "[FAIL]" in output


def test_format_chain_empty():
    assert format_chain([]) == "(empty chain)"
