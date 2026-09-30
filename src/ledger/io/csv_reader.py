"""Read transactions from a CSV file with header date,amount,category,memo."""

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from os import PathLike

from ledger.core.transaction import Transaction
from ledger.core.validation import InvalidTransaction

HEADER = ["date", "amount", "category", "memo"]


class CsvFormatError(ValueError):
    """A CSV row could not be turned into a Transaction.

    ``line_number`` is the 1-based line in the file; the header is line 1.
    """

    def __init__(self, line_number: int, reason: str) -> None:
        super().__init__(f"line {line_number}: {reason}")
        self.line_number = line_number
        self.reason = reason


def read_csv(path: str | PathLike[str]) -> list[Transaction]:
    """Parse every data row; the first malformed row raises CsvFormatError."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != HEADER:
            raise CsvFormatError(1, f"expected header {','.join(HEADER)}, got {header}")
        transactions = []
        for row in reader:
            if not row:
                continue
            transactions.append(_parse_row(row, reader.line_num))
        return transactions


def _parse_row(row: list[str], line_number: int) -> Transaction:
    if len(row) != len(HEADER):
        raise CsvFormatError(line_number, f"expected {len(HEADER)} columns, got {len(row)}")
    raw_date, raw_amount, category, memo = row
    try:
        parsed_date = date.fromisoformat(raw_date)
    except ValueError:
        raise CsvFormatError(line_number, f"invalid date {raw_date!r}") from None
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation:
        raise CsvFormatError(line_number, f"invalid amount {raw_amount!r}") from None
    try:
        return Transaction(parsed_date, amount, category, memo)
    except InvalidTransaction as e:
        raise CsvFormatError(line_number, str(e)) from e
