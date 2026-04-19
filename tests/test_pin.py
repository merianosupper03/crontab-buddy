import pytest
from pathlib import Path
from crontab_buddy.pin import pin_expression, unpin_expression, get_pins, is_pinned, clear_pins


@pytest.fixture
def tmp_pins(tmp_path):
    return tmp_path / "pins.json"


def test_pin_new_expression(tmp_pins):
    assert pin_expression("0 * * * *", path=tmp_pins) is True
    assert "0 * * * *" in get_pins(path=tmp_pins)


def test_pin_duplicate_returns_false(tmp_pins):
    pin_expression("0 * * * *", path=tmp_pins)
    assert pin_expression("0 * * * *", path=tmp_pins) is False


def test_unpin_existing(tmp_pins):
    pin_expression("0 0 * * *", path=tmp_pins)
    assert unpin_expression("0 0 * * *", path=tmp_pins) is True
    assert "0 0 * * *" not in get_pins(path=tmp_pins)


def test_unpin_missing_returns_false(tmp_pins):
    assert unpin_expression("5 5 * * *", path=tmp_pins) is False


def test_get_pins_empty(tmp_pins):
    assert get_pins(path=tmp_pins) == []


def test_get_pins_multiple(tmp_pins):
    pin_expression("0 * * * *", path=tmp_pins)
    pin_expression("0 0 * * *", path=tmp_pins)
    pins = get_pins(path=tmp_pins)
    assert len(pins) == 2


def test_is_pinned_true(tmp_pins):
    pin_expression("*/5 * * * *", path=tmp_pins)
    assert is_pinned("*/5 * * * *", path=tmp_pins) is True


def test_is_pinned_false(tmp_pins):
    assert is_pinned("*/5 * * * *", path=tmp_pins) is False


def test_clear_pins(tmp_pins):
    pin_expression("0 * * * *", path=tmp_pins)
    pin_expression("0 0 * * *", path=tmp_pins)
    clear_pins(path=tmp_pins)
    assert get_pins(path=tmp_pins) == []


def test_order_preserved(tmp_pins):
    exprs = ["0 * * * *", "0 0 * * *", "*/15 * * * *"]
    for e in exprs:
        pin_expression(e, path=tmp_pins)
    assert get_pins(path=tmp_pins) == exprs
