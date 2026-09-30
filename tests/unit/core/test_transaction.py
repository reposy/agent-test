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


def test_rejects_zero_amount():
    with pytest.raises(InvalidTransaction):
        Transaction(date(2026, 1, 5), Decimal("0"), "식비")


def test_rejects_negative_amount():
    with pytest.raises(InvalidTransaction):
        Transaction(date(2026, 1, 5), Decimal("-500"), "식비")


def test_rejects_float_amount():
    with pytest.raises(InvalidTransaction):
        Transaction(date(2026, 1, 5), 12.5, "식비")


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
