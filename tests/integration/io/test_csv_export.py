"""Round-trip scenarios: read a real fixture, write it with write_csv, read it again."""

from pathlib import Path

import pytest

import ledger.io
from ledger.core import InMemoryLedger
from ledger.io import read_csv

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("fixture", ["valid.csv", "bom_blank_lines.csv"])
def test_fixture_survives_read_write_read(tmp_path, fixture):
    original = read_csv(FIXTURES / fixture)
    out = tmp_path / "export.csv"
    ledger.io.write_csv(original, out)
    assert read_csv(out) == original


def test_ledger_contents_can_be_exported_and_reloaded(tmp_path):
    ledger_ = InMemoryLedger()
    for t in read_csv(FIXTURES / "valid.csv"):
        ledger_.add(t)
    out = tmp_path / "export.csv"
    ledger.io.write_csv(ledger_.all(), out)
    assert read_csv(out) == ledger_.all()


def test_exported_file_is_stable_when_exported_again(tmp_path):
    first, second = tmp_path / "first.csv", tmp_path / "second.csv"
    ledger.io.write_csv(read_csv(FIXTURES / "valid.csv"), first)
    ledger.io.write_csv(read_csv(first), second)
    assert first.read_bytes() == second.read_bytes()
