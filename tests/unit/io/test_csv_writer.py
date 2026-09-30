import csv
import io
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

import ledger.io
from ledger.core.transaction import Transaction
from ledger.io.csv_reader import read_csv

BOM = b"\xef\xbb\xbf"
HEADER = ["date", "amount", "category", "memo"]


def tx(amount: str = "1", memo: str = "", category: str = "식비", day: int = 5) -> Transaction:
    return Transaction(date(2026, 1, day), Decimal(amount), category, memo)


@pytest.fixture
def path(tmp_path):
    return tmp_path / "out.csv"


def decoded_text(path) -> str:
    """File text after the BOM; fails if the BOM is missing."""
    raw = path.read_bytes()
    assert raw.startswith(BOM)
    return raw[len(BOM) :].decode("utf-8")


def records(path) -> list[list[str]]:
    """Parsed CSV fields, independent of how the writer chose to quote them."""
    return list(csv.reader(io.StringIO(decoded_text(path), newline="")))


def assert_only_crlf_line_endings(text: str, record_count: int) -> None:
    """For files whose fields contain no newlines: every record ends in CRLF, nothing else."""
    assert text.endswith("\r\n")
    assert text.count("\r\n") == record_count
    stripped = text.replace("\r\n", "")
    assert "\r" not in stripped
    assert "\n" not in stripped


def test_write_csv_is_exported_from_ledger_io():
    assert "write_csv" in ledger.io.__all__
    assert callable(ledger.io.write_csv)


def test_written_file_reads_back_as_the_same_transactions_in_the_same_order(path):
    transactions = [
        tx("12000", "점심", day=20),
        tx("3500.50", "", category="교통", day=3),
        tx("12000", "점심", day=20),
    ]
    assert ledger.io.write_csv(transactions, path) is None
    assert read_csv(path) == transactions


def test_accepts_str_path(path):
    ledger.io.write_csv([tx()], str(path))
    assert read_csv(path) == [tx()]


def test_accepts_any_iterable_such_as_a_generator(path):
    transactions = [tx("1", day=1), tx("2", day=2)]
    ledger.io.write_csv((t for t in transactions), path)
    assert read_csv(path) == transactions


def test_empty_list_writes_header_only_and_reads_back_as_empty_list(path):
    ledger.io.write_csv([], path)
    assert records(path) == [HEADER]
    assert_only_crlf_line_endings(decoded_text(path), record_count=1)
    assert read_csv(path) == []


def test_file_is_utf8_with_bom_and_crlf_line_endings(path):
    ledger.io.write_csv([tx("12000", "점심"), tx("1", "", day=6)], path)
    assert records(path) == [
        HEADER,
        ["2026-01-05", "12000", "식비", "점심"],
        ["2026-01-06", "1", "식비", ""],
    ]
    assert_only_crlf_line_endings(decoded_text(path), record_count=3)


@pytest.mark.parametrize(
    "memo",
    [
        "김밥, 라면",
        'say "hi"',
        '"',
        '","',
        "첫 줄\n둘째 줄",
        "첫 줄\r\n둘째 줄",
        "첫 줄\r둘째 줄",
        "\n",
        "끝 줄바꿈\n",
        "  앞뒤 공백  ",
        " ",
        "",
        '콤마, "따옴표"\r\n그리고 줄바꿈',
    ],
)
def test_memo_with_commas_quotes_or_newlines_round_trips_exactly(path, memo):
    ledger.io.write_csv([tx(memo=memo), tx("2", "다음 행", day=6)], path)
    assert read_csv(path) == [tx(memo=memo), tx("2", "다음 행", day=6)]


@pytest.mark.parametrize("category", ["외식, 배달", 'a "b"', "  식비  ", "여러\n줄"])
def test_category_with_special_characters_round_trips_exactly(path, category):
    ledger.io.write_csv([tx(category=category)], path)
    assert read_csv(path) == [tx(category=category)]


@pytest.mark.parametrize(
    ("amount", "written"),
    [
        ("12000", "12000"),
        ("0.10", "0.10"),
        ("3500.50", "3500.50"),
        ("100.00", "100.00"),
        ("1E+3", "1000"),
        ("1.20E+2", "120"),
        ("1.5E-7", "0.00000015"),
    ],
)
def test_amount_is_written_in_fixed_point_notation(path, amount, written):
    ledger.io.write_csv([tx(amount)], path)
    assert [row[1] for row in records(path)[1:]] == [written]
    [t] = read_csv(path)
    assert t.amount == Decimal(amount)


def test_overwrites_existing_file_completely(path):
    path.write_text("old content that is much longer than the new file\n" * 50)
    ledger.io.write_csv([tx()], path)
    assert records(path)[0] == HEADER
    assert read_csv(path) == [tx()]


LOOKS_LIKE_TRANSACTION = SimpleNamespace(
    date=date(2026, 1, 5), amount=Decimal("1"), category="식비", memo=""
)


@pytest.mark.parametrize(
    "bad",
    [
        None,
        "2026-01-05,1,식비,",
        (date(2026, 1, 5), Decimal("1"), "식비", ""),
        {"amount": 1},
        LOOKS_LIKE_TRANSACTION,
    ],
)
def test_non_transaction_element_raises_type_error_and_creates_no_file(path, bad):
    with pytest.raises(TypeError):
        ledger.io.write_csv([tx(), bad], path)
    assert not path.exists()


def test_non_transaction_element_leaves_existing_file_untouched(path):
    path.write_bytes(b"previous bytes")
    with pytest.raises(TypeError):
        ledger.io.write_csv((t for t in [tx("1"), tx("2"), object()]), path)
    assert path.read_bytes() == b"previous bytes"
