from datetime import date
from decimal import Decimal

from ledger.core.transaction import Transaction
from ledger.report.summary import monthly_totals, total


def tx(day: date, amount: str) -> Transaction:
    return Transaction(day, Decimal(amount), "식비")


def test_total_of_no_transactions_is_zero():
    assert total([]) == Decimal("0")


def test_total_sums_all_amounts():
    assert total([tx(date(2026, 1, 1), "1000"), tx(date(2026, 2, 1), "2500")]) == Decimal("3500")


def test_total_keeps_decimal_precision():
    result = total([tx(date(2026, 1, 1), "0.1"), tx(date(2026, 1, 2), "0.2")])
    assert result == Decimal("0.3")
    assert isinstance(result, Decimal)


def test_total_accepts_any_iterable():
    assert total(tx(date(2026, 1, d), "1") for d in (1, 2, 3)) == Decimal("3")


def test_monthly_totals_of_no_transactions_is_empty():
    assert monthly_totals([]) == {}


def test_monthly_totals_groups_amounts_by_year_and_month():
    result = monthly_totals([
        tx(date(2026, 1, 1), "1000"),
        tx(date(2026, 1, 31), "500"),
        tx(date(2026, 2, 1), "300"),
    ])
    assert result == {"2026-01": Decimal("1500"), "2026-02": Decimal("300")}


def test_monthly_totals_separates_same_month_in_different_years():
    result = monthly_totals([tx(date(2025, 1, 1), "1"), tx(date(2026, 1, 1), "2")])
    assert result == {"2025-01": Decimal("1"), "2026-01": Decimal("2")}


def test_monthly_totals_keys_are_ordered_by_month_regardless_of_input_order():
    result = monthly_totals([
        tx(date(2026, 3, 1), "1"),
        tx(date(2025, 12, 1), "1"),
        tx(date(2026, 1, 1), "1"),
    ])
    assert list(result) == ["2025-12", "2026-01", "2026-03"]
