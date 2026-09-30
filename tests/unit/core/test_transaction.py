import dataclasses
from datetime import date
from decimal import Decimal

import pytest

from ledger.core.transaction import Transaction
from ledger.core.validation import InvalidTransaction


def test_creates_transaction_with_all_fields():
    t = Transaction(date(2026, 1, 5), Decimal("12000"), "식비", "점심")
    assert t.date == date(2026, 1, 5)
    assert t.amount == Decimal("12000")
    assert t.category == "식비"
    assert t.memo == "점심"


def test_memo_defaults_to_empty_string():
    assert Transaction(date(2026, 1, 5), Decimal("1"), "기타").memo == ""


@pytest.mark.parametrize("value", ["0", "-0"])
def test_rejects_zero_amount(value):
    with pytest.raises(InvalidTransaction):
        Transaction(date(2026, 1, 5), Decimal(value), "식비")


def test_accepts_negative_amount_as_refund_and_keeps_its_sign():
    t = Transaction(date(2026, 1, 5), Decimal("-500"), "식비", "환불")
    assert t.amount == Decimal("-500")


def test_negative_amount_keeps_its_decimal_places():
    t = Transaction(date(2026, 1, 5), Decimal("-3500.50"), "교통")
    assert str(t.amount) == "-3500.50"


def test_rejects_float_amount():
    with pytest.raises(InvalidTransaction):
        Transaction(date(2026, 1, 5), 12.5, "식비")


@pytest.mark.parametrize("value", [-12.5, -500])
def test_rejects_negative_non_decimal_amount(value):
    with pytest.raises(InvalidTransaction):
        Transaction(date(2026, 1, 5), value, "식비")


def test_rejects_blank_category():
    with pytest.raises(InvalidTransaction):
        Transaction(date(2026, 1, 5), Decimal("1"), "   ")


def test_rejects_non_date_date():
    with pytest.raises(InvalidTransaction):
        Transaction("2026-01-05", Decimal("1"), "식비")


def test_is_immutable():
    t = Transaction(date(2026, 1, 5), Decimal("1"), "식비")
    with pytest.raises(dataclasses.FrozenInstanceError):
        t.amount = Decimal("2")


def test_transactions_with_equal_fields_are_equal():
    a = Transaction(date(2026, 1, 5), Decimal("1.0"), "식비", "x")
    b = Transaction(date(2026, 1, 5), Decimal("1.0"), "식비", "x")
    assert a == b
