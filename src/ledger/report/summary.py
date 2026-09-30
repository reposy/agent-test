"""Totals over an iterable of transactions."""

from collections.abc import Iterable
from decimal import Decimal

from ledger.core.transaction import Transaction


def total(transactions: Iterable[Transaction]) -> Decimal:
    """Sum of all amounts; Decimal("0") for no transactions."""
    return sum((t.amount for t in transactions), Decimal("0"))


def monthly_totals(transactions: Iterable[Transaction]) -> dict[str, Decimal]:
    """Sum of amounts per month, keyed "YYYY-MM" and ordered by month."""
    totals: dict[str, Decimal] = {}
    for t in transactions:
        key = f"{t.date.year:04d}-{t.date.month:02d}"
        totals[key] = totals.get(key, Decimal("0")) + t.amount
    return dict(sorted(totals.items()))
