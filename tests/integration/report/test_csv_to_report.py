"""Scenarios that flow from a CSV file through the ledger into reports."""

from datetime import date
from decimal import Decimal

import pytest

from ledger.core import InMemoryLedger
from ledger.io import CsvFormatError, read_csv
from ledger.report import monthly_totals, total

CSV = """\
date,amount,category,memo
2025-12-31,50000,선물,연말
2026-01-01,12000,식비,"떡국, 만두"
2026-01-15,1250.50,교통,
2026-01-31,30000,통신,휴대폰
2026-02-01,8900,식비,
2026-02-28,100000,주거,관리비
"""


@pytest.fixture
def csv_path(tmp_path):
    path = tmp_path / "ledger.csv"
    path.write_text(CSV, encoding="utf-8")
    return path


def test_csv_total_equals_sum_of_all_rows(csv_path):
    assert total(read_csv(csv_path)) == Decimal("202150.50")


def test_csv_monthly_totals_span_year_boundary(csv_path):
    assert monthly_totals(read_csv(csv_path)) == {
        "2025-12": Decimal("50000"),
        "2026-01": Decimal("43250.50"),
        "2026-02": Decimal("108900"),
    }


def test_monthly_totals_add_up_to_total(csv_path):
    transactions = read_csv(csv_path)
    assert sum(monthly_totals(transactions).values(), Decimal("0")) == total(transactions)


def test_ledger_range_from_csv_feeds_report(csv_path):
    ledger = InMemoryLedger()
    for t in read_csv(csv_path):
        ledger.add(t)
    january = ledger.between(date(2026, 1, 1), date(2026, 1, 31))
    assert total(january) == Decimal("43250.50")
    assert monthly_totals(january) == {"2026-01": Decimal("43250.50")}


def test_malformed_row_stops_import_before_any_report(tmp_path):
    path = tmp_path / "broken.csv"
    path.write_text(CSV + "2026-03-01,0,식비,무료\n", encoding="utf-8")
    with pytest.raises(CsvFormatError) as excinfo:
        read_csv(path)
    assert excinfo.value.line_number == 8


REFUND_CSV = """\
date,amount,category,memo
2026-01-10,99000,쇼핑,"겨울 코트, 할인"
2026-01-31,-99000,쇼핑,코트 반품
2026-02-01,-3000.50,식비,1월 배달 환불
2026-02-01,12000,식비,
2026-02-28,50000,주거,관리비
2026-03-02,-20000,주거,관리비 정산 환급
"""


@pytest.fixture
def refund_csv_path(tmp_path):
    path = tmp_path / "refunds.csv"
    path.write_text(REFUND_CSV, encoding="utf-8")
    return path


def test_csv_refund_rows_are_imported_with_negative_amounts(refund_csv_path):
    amounts = [t.amount for t in read_csv(refund_csv_path)]
    assert amounts == [
        Decimal("99000"),
        Decimal("-99000"),
        Decimal("-3000.50"),
        Decimal("12000"),
        Decimal("50000"),
        Decimal("-20000"),
    ]


def test_csv_total_nets_refunds_against_spending(refund_csv_path):
    assert total(read_csv(refund_csv_path)) == Decimal("38999.50")


def test_csv_monthly_totals_net_refunds_per_month(refund_csv_path):
    assert monthly_totals(read_csv(refund_csv_path)) == {
        "2026-01": Decimal("0"),
        "2026-02": Decimal("58999.50"),
        "2026-03": Decimal("-20000"),
    }


def test_monthly_totals_with_refunds_add_up_to_total(refund_csv_path):
    transactions = read_csv(refund_csv_path)
    assert sum(monthly_totals(transactions).values(), Decimal("0")) == total(transactions)


def test_ledger_range_with_refunds_feeds_report(refund_csv_path):
    ledger = InMemoryLedger()
    for t in read_csv(refund_csv_path):
        ledger.add(t)
    assert len(ledger.all()) == 6
    february_on = ledger.between(date(2026, 2, 1), date(2026, 3, 31))
    assert [t.amount for t in february_on] == [
        Decimal("-3000.50"),
        Decimal("12000"),
        Decimal("50000"),
        Decimal("-20000"),
    ]
    assert total(february_on) == Decimal("38999.50")
    assert monthly_totals(february_on) == {
        "2026-02": Decimal("58999.50"),
        "2026-03": Decimal("-20000"),
    }


def test_negative_zero_row_stops_import(tmp_path):
    path = tmp_path / "negative_zero.csv"
    path.write_text(REFUND_CSV + "2026-03-05,-0,식비,\n", encoding="utf-8")
    with pytest.raises(CsvFormatError, match="zero") as excinfo:
        read_csv(path)
    assert excinfo.value.line_number == 8
