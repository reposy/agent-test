"""An in-memory transaction store."""

from datetime import date

from ledger.core.transaction import Transaction


class InMemoryLedger:
    """Keeps transactions in insertion order."""

    def __init__(self) -> None:
        self._transactions: list[Transaction] = []

    def add(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise TypeError(f"expected Transaction, got {type(transaction).__name__}")
        self._transactions.append(transaction)

    def all(self) -> list[Transaction]:
        return list(self._transactions)

    def between(self, start: date, end: date) -> list[Transaction]:
        """Return transactions with start <= date <= end (both ends inclusive)."""
        if start > end:
            raise ValueError(f"start {start} is after end {end}")
        return [t for t in self._transactions if start <= t.date <= end]
