from datetime import date
from decimal import Decimal

import pytest

from ledger.core.ledger import InMemoryLedger
from ledger.core.transaction import Transaction


def tx(day: date, amount: str = "1000") -> Transaction:
    return Transaction(day, Decimal(amount), "식비")


def test_new_ledger_is_empty():
    assert InMemoryLedger().all() == []


def test_all_returns_added_transactions_in_insertion_order():
    ledger = InMemoryLedger()
    first, second = tx(date(2026, 2, 1)), tx(date(2026, 1, 1))
    ledger.add(first)
    ledger.add(second)
    assert ledger.all() == [first, second]


def test_all_returns_a_copy_that_does_not_affect_the_ledger():
    ledger = InMemoryLedger()
    ledger.add(tx(date(2026, 1, 1)))
    ledger.all().clear()
    assert len(ledger.all()) == 1


def test_add_rejects_non_transaction():
    with pytest.raises(TypeError):
        InMemoryLedger().add({"amount": Decimal("1")})


def test_between_includes_both_start_and_end_dates():
    ledger = InMemoryLedger()
    before, start, middle, end, after = (
        tx(date(2026, 1, d)) for d in (9, 10, 15, 20, 21)
    )
    for t in (before, start, middle, end, after):
        ledger.add(t)
    assert ledger.between(date(2026, 1, 10), date(2026, 1, 20)) == [start, middle, end]


def test_between_with_same_start_and_end_returns_that_day():
    ledger = InMemoryLedger()
    day = tx(date(2026, 3, 1))
    ledger.add(day)
    ledger.add(tx(date(2026, 3, 2)))
    assert ledger.between(date(2026, 3, 1), date(2026, 3, 1)) == [day]


def test_between_returns_empty_list_when_nothing_matches():
    ledger = InMemoryLedger()
    ledger.add(tx(date(2026, 1, 1)))
    assert ledger.between(date(2026, 2, 1), date(2026, 2, 28)) == []


def test_between_rejects_start_after_end():
    with pytest.raises(ValueError):
        InMemoryLedger().between(date(2026, 2, 1), date(2026, 1, 1))
