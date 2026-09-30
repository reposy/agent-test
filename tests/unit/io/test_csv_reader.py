from datetime import date
from decimal import Decimal

import pytest

from ledger.core.transaction import Transaction
from ledger.io.csv_reader import CsvFormatError, read_csv

HEADER = "date,amount,category,memo\n"


@pytest.fixture
def write_csv(tmp_path):
    def write(body: str, header: str = HEADER, encoding: str = "utf-8"):
        path = tmp_path / "ledger.csv"
        path.write_text(header + body, encoding=encoding)
        return path

    return write


def test_reads_rows_into_transactions(write_csv):
    path = write_csv("2026-01-05,12000,식비,점심\n2026-01-06,3500.50,교통,\n")
    assert read_csv(path) == [
        Transaction(date(2026, 1, 5), Decimal("12000"), "식비", "점심"),
        Transaction(date(2026, 1, 6), Decimal("3500.50"), "교통", ""),
    ]


def test_parses_amount_as_decimal_not_float(write_csv):
    [t] = read_csv(write_csv("2026-01-05,0.10,식비,\n"))
    assert isinstance(t.amount, Decimal)
    assert str(t.amount) == "0.10"


def test_reads_negative_amount_as_refund_keeping_sign_and_decimal_places(write_csv):
    path = write_csv(
        "2026-01-05,12000,식비,점심\n2026-01-06,-100,식비,환불\n2026-01-07,-0.50,교통,\n"
    )
    assert read_csv(path) == [
        Transaction(date(2026, 1, 5), Decimal("12000"), "식비", "점심"),
        Transaction(date(2026, 1, 6), Decimal("-100"), "식비", "환불"),
        Transaction(date(2026, 1, 7), Decimal("-0.50"), "교통", ""),
    ]
    assert [str(t.amount) for t in read_csv(path)] == ["12000", "-100", "-0.50"]


def test_accepts_str_path(write_csv):
    assert len(read_csv(str(write_csv("2026-01-05,1,식비,\n")))) == 1


def test_header_only_file_returns_empty_list(write_csv):
    assert read_csv(write_csv("")) == []


def test_skips_blank_lines(write_csv):
    assert len(read_csv(write_csv("2026-01-05,1,식비,\n\n2026-01-06,1,식비,\n"))) == 2


def test_reads_quoted_memo_containing_comma(write_csv):
    [t] = read_csv(write_csv('2026-01-05,1,식비,"김밥, 라면"\n'))
    assert t.memo == "김밥, 라면"


def test_ignores_utf8_byte_order_mark(write_csv):
    assert len(read_csv(write_csv("2026-01-05,1,식비,\n", encoding="utf-8-sig"))) == 1


def test_rejects_wrong_header_as_line_1(write_csv):
    with pytest.raises(CsvFormatError) as excinfo:
        read_csv(write_csv("2026-01-05,1,식비,\n", header="day,amount,category,memo\n"))
    assert excinfo.value.line_number == 1


def test_rejects_empty_file_as_line_1(write_csv):
    with pytest.raises(CsvFormatError) as excinfo:
        read_csv(write_csv("", header=""))
    assert excinfo.value.line_number == 1


@pytest.mark.parametrize(
    ("bad_row", "reason"),
    [
        ("2026-13-01,1,식비,", "invalid date"),
        ("not-a-date,1,식비,", "invalid date"),
        ("2026-01-05,abc,식비,", "invalid amount"),
        ("2026-01-05,,식비,", "invalid amount"),
        ("2026-01-05,1,식비", "expected 4 columns"),
        ("2026-01-05,1,식비,memo,extra", "expected 4 columns"),
        ("2026-01-05,0,식비,", "zero"),
        ("2026-01-05,-0,식비,", "zero"),
        ("2026-01-05,(100),식비,", "invalid amount"),
        ("2026-01-05,1, ,", "blank"),
    ],
)
def test_reports_line_number_of_malformed_row(write_csv, bad_row, reason):
    path = write_csv(f"2026-01-05,1,식비,\n{bad_row}\n")
    with pytest.raises(CsvFormatError, match=reason) as excinfo:
        read_csv(path)
    assert excinfo.value.line_number == 3
    assert "line 3" in str(excinfo.value)


def test_line_number_counts_blank_lines(write_csv):
    with pytest.raises(CsvFormatError) as excinfo:
        read_csv(write_csv("2026-01-05,1,식비,\n\nbad,1,식비,\n"))
    assert excinfo.value.line_number == 4
