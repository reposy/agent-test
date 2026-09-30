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


def test_total_subtracts_refunds():
    result = total([tx(date(2026, 1, 1), "12000"), tx(date(2026, 1, 2), "-2000.50")])
    assert result == Decimal("9999.50")


def test_total_is_negative_when_refunds_exceed_spending():
    assert total([tx(date(2026, 1, 1), "1000"), tx(date(2026, 1, 2), "-3000")]) == Decimal("-2000")


def test_total_of_only_refunds_is_negative():
    assert total([tx(date(2026, 1, 1), "-0.1"), tx(date(2026, 1, 2), "-0.2")]) == Decimal("-0.3")


def test_total_is_zero_when_refund_cancels_purchase():
    assert total([tx(date(2026, 1, 1), "5000"), tx(date(2026, 1, 9), "-5000")]) == Decimal("0")


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


def test_monthly_totals_subtract_refunds_in_their_own_month():
    result = monthly_totals([
        tx(date(2026, 1, 10), "30000"),
        tx(date(2026, 1, 20), "-5000"),
        tx(date(2026, 2, 3), "12000"),
        tx(date(2026, 2, 5), "-12000.50"),
        tx(date(2026, 3, 1), "700"),
    ])
    assert result == {
        "2026-01": Decimal("25000"),
        "2026-02": Decimal("-0.50"),
        "2026-03": Decimal("700"),
    }


def test_monthly_totals_keep_month_whose_refunds_cancel_out_to_zero():
    result = monthly_totals([
        tx(date(2026, 1, 1), "100"),
        tx(date(2026, 2, 1), "5000"),
        tx(date(2026, 2, 15), "-5000"),
        tx(date(2026, 3, 1), "200"),
    ])
    assert result == {
        "2026-01": Decimal("100"),
        "2026-02": Decimal("0"),
        "2026-03": Decimal("200"),
    }
    assert list(result) == ["2026-01", "2026-02", "2026-03"]


def test_monthly_totals_include_month_with_only_refunds():
    result = monthly_totals([tx(date(2026, 2, 1), "-300"), tx(date(2026, 1, 1), "1000")])
    assert result == {"2026-01": Decimal("1000"), "2026-02": Decimal("-300")}
    assert list(result) == ["2026-01", "2026-02"]
