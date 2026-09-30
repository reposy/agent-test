"""The Transaction value object."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ledger.core.validation import (
    validate_amount,
    validate_category,
    validate_date,
    validate_memo,
)


@dataclass(frozen=True, slots=True)
class Transaction:
    """A single ledger entry. Invalid values raise InvalidTransaction on creation."""

    date: date
    amount: Decimal
    category: str
    memo: str = ""

    def __post_init__(self) -> None:
        validate_date(self.date)
        validate_amount(self.amount)
        validate_category(self.category)
        validate_memo(self.memo)
