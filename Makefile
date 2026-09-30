PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
RUFF ?= $(PYTHON) -m ruff

# Optional JUnit XML output path, e.g. `make test JUNIT_XML=reports/junit.xml`
JUNIT_XML ?=
PYTEST_ARGS ?=
JUNIT_FLAG = $(if $(JUNIT_XML),--junitxml=$(JUNIT_XML),)

.PHONY: install lint unit integration test

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

lint:
	$(RUFF) check src tests

unit:
	$(PYTEST) tests/unit $(JUNIT_FLAG) $(PYTEST_ARGS)

integration:
	$(PYTEST) tests/integration $(JUNIT_FLAG) $(PYTEST_ARGS)

test:
	$(PYTEST) tests $(JUNIT_FLAG) $(PYTEST_ARGS)
