"""Validation rules for transaction fields."""

from datetime import date
from decimal import Decimal


class InvalidTransaction(ValueError):
    """Raised when a transaction violates a domain rule."""


def validate_date(value: object) -> None:
    if not isinstance(value, date):
        raise InvalidTransaction(f"date must be a datetime.date, got {type(value).__name__}")


def validate_amount(value: object) -> None:
    if not isinstance(value, Decimal):
        raise InvalidTransaction(f"amount must be a Decimal, got {type(value).__name__}")
    if not value.is_finite():
        raise InvalidTransaction(f"amount must be finite, got {value}")
    if value <= 0:
        raise InvalidTransaction(f"amount must be greater than zero, got {value}")


def validate_category(value: object) -> None:
    if not isinstance(value, str):
        raise InvalidTransaction(f"category must be a str, got {type(value).__name__}")
    if not value.strip():
        raise InvalidTransaction("category must not be blank")


def validate_memo(value: object) -> None:
    if not isinstance(value, str):
        raise InvalidTransaction(f"memo must be a str, got {type(value).__name__}")
