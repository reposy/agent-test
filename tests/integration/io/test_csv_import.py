"""Scenarios that read real CSV fixture files from tests/integration/io/fixtures/."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ledger.core import InMemoryLedger, Transaction
from ledger.io import CsvFormatError, read_csv
from ledger.report import total

FIXTURES = Path(__file__).parent / "fixtures"


def load_ledger(path: Path) -> InMemoryLedger:
    ledger = InMemoryLedger()
    for t in read_csv(path):
        ledger.add(t)
    return ledger


def test_valid_file_flows_into_ledger_in_file_order():
    ledger = load_ledger(FIXTURES / "valid.csv")
    assert [t.date for t in ledger.all()] == [
        date(2026, 1, 3),
        date(2026, 1, 10),
        date(2026, 1, 31),
        date(2026, 2, 1),
        date(2026, 2, 14),
        date(2026, 3, 1),
    ]


def test_valid_file_between_returns_rows_in_range_including_both_ends():
    ledger = load_ledger(FIXTURES / "valid.csv")
    february_edge = ledger.between(date(2026, 1, 31), date(2026, 2, 14))
    assert february_edge == [
        Transaction(date(2026, 1, 31), Decimal("55000"), "통신", "휴대폰 요금"),
        Transaction(date(2026, 2, 1), Decimal("1250.50"), "교통", "버스"),
        Transaction(date(2026, 2, 14), Decimal("30000"), "선물", ""),
    ]
    assert total(february_edge) == Decimal("86250.50")


def test_valid_file_keeps_quoted_memo_with_comma():
    [t] = load_ledger(FIXTURES / "valid.csv").between(date(2026, 1, 10), date(2026, 1, 10))
    assert t.memo == "김밥, 라면"


def test_bom_fixture_really_starts_with_bom_and_has_blank_lines():
    raw = (FIXTURES / "bom_blank_lines.csv").read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    assert b"\r\n\r\n" in raw


def test_excel_style_file_with_bom_and_blank_lines_is_read_cleanly():
    assert read_csv(FIXTURES / "bom_blank_lines.csv") == [
        Transaction(date(2026, 1, 5), Decimal("12000"), "식비", "점심"),
        Transaction(date(2026, 1, 6), Decimal("3500.50"), "교통", ""),
        Transaction(date(2026, 2, 1), Decimal("99000"), "쇼핑", "겨울 코트, 할인"),
    ]


def test_excel_style_file_flows_into_ledger_between():
    ledger = load_ledger(FIXTURES / "bom_blank_lines.csv")
    assert total(ledger.between(date(2026, 1, 1), date(2026, 1, 31))) == Decimal("15500.50")


def test_malformed_row_raises_csv_format_error_with_file_line_number():
    # Line 3 is blank, so the bad row is file line 4 even though it is the 2nd data row.
    with pytest.raises(CsvFormatError, match="expected 4 columns") as excinfo:
        read_csv(FIXTURES / "malformed_row.csv")
    assert excinfo.value.line_number == 4
    assert str(excinfo.value).startswith("line 4:")


def test_malformed_row_leaves_nothing_in_ledger():
    ledger = InMemoryLedger()
    with pytest.raises(CsvFormatError):
        for t in read_csv(FIXTURES / "malformed_row.csv"):
            ledger.add(t)
    assert ledger.all() == []
