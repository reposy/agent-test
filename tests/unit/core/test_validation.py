from datetime import date
from decimal import Decimal

import pytest

from ledger.core.validation import (
    InvalidTransaction,
    validate_amount,
    validate_category,
    validate_date,
    validate_memo,
)


def test_accepts_positive_decimal_amount():
    validate_amount(Decimal("0.01"))


def test_rejects_zero_amount():
    with pytest.raises(InvalidTransaction, match="greater than zero"):
        validate_amount(Decimal("0"))


def test_rejects_negative_amount():
    with pytest.raises(InvalidTransaction, match="greater than zero"):
        validate_amount(Decimal("-1"))


def test_rejects_float_amount():
    with pytest.raises(InvalidTransaction, match="Decimal"):
        validate_amount(1.5)


def test_rejects_int_amount():
    with pytest.raises(InvalidTransaction, match="Decimal"):
        validate_amount(10)


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_rejects_non_finite_amount(value):
    with pytest.raises(InvalidTransaction, match="finite"):
        validate_amount(Decimal(value))


def test_accepts_non_blank_category():
    validate_category("식비")


@pytest.mark.parametrize("value", ["", " ", "\t\n"])
def test_rejects_blank_category(value):
    with pytest.raises(InvalidTransaction, match="blank"):
        validate_category(value)


def test_rejects_non_string_category():
    with pytest.raises(InvalidTransaction, match="str"):
        validate_category(None)


def test_accepts_date_value():
    validate_date(date(2026, 1, 1))


def test_rejects_string_date():
    with pytest.raises(InvalidTransaction, match="date"):
        validate_date("2026-01-01")


def test_accepts_empty_memo():
    validate_memo("")


def test_rejects_non_string_memo():
    with pytest.raises(InvalidTransaction, match="memo"):
        validate_memo(None)


def test_invalid_transaction_is_a_value_error():
    assert issubclass(InvalidTransaction, ValueError)
