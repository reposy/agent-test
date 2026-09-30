# ledger

가계부(household ledger) 파이썬 라이브러리. AI 에이전트 오케스트레이터의 테스트 대상으로 쓰는 시드 레포라서 기능은 최소한이고, 구조와 테스트에 무게를 뒀습니다.

- Python 3.12, 런타임 의존성 없음 (표준 라이브러리만)
- 금액은 항상 `decimal.Decimal` (float 거부)
- 결정론: 현재 시각, 랜덤, 네트워크 사용 안 함

## 구조

```
src/ledger/
  core/        transaction.py (Transaction), validation.py (InvalidTransaction, 검증), ledger.py (InMemoryLedger)
  report/      summary.py (total, monthly_totals)
  io/          csv_reader.py (read_csv, CsvFormatError)
tests/
  unit/<패키지>/test_<모듈>.py         src/ledger/<패키지>/<모듈>.py 와 1:1 대응
  integration/<패키지>/test_*.py       CSV → ledger → report 시나리오
```

## 설치

```sh
python3.12 -m venv .venv
source .venv/bin/activate
make install        # pip install -r requirements-dev.txt (pytest, ruff)
```

## 검증

```sh
make lint           # ruff check
make unit           # tests/unit
make integration    # tests/integration
make test           # 전체 테스트
make lint test      # CI와 동일
```

JUnit XML 리포트가 필요하면 `JUNIT_XML`로 경로를 넘깁니다. 추가 pytest 인자는 `PYTEST_ARGS`로 넘깁니다.

```sh
make test JUNIT_XML=reports/junit.xml
make unit JUNIT_XML=reports/unit.xml PYTEST_ARGS="-k csv"
```

venv를 활성화하지 않았다면 `make test PYTHON=.venv/bin/python`처럼 인터프리터를 지정할 수 있습니다.

## 사용 예

```python
from datetime import date
from ledger.core import InMemoryLedger
from ledger.io import read_csv
from ledger.report import monthly_totals, total

ledger = InMemoryLedger()
for t in read_csv("ledger.csv"):       # 헤더: date,amount,category,memo
    ledger.add(t)

january = ledger.between(date(2026, 1, 1), date(2026, 1, 31))  # 양 끝 포함
total(january)             # Decimal('43250.50')
monthly_totals(ledger.all())  # {'2026-01': Decimal(...), ...}
```

형식이 잘못된 CSV 행은 `CsvFormatError`를 던지며, `line_number`에 파일 기준 줄 번호(헤더 = 1)가 담깁니다.

## CI

GitHub Actions(`.github/workflows/ci.yml`)가 `main` push와 `main` 대상 PR에서 `make lint test`를 실행합니다.
