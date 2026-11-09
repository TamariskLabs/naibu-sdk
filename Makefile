.PHONY: help install lint format typecheck test cov check build clean

help:
	@echo "Targets:"
	@echo "  install    Install the package with dev dependencies"
	@echo "  lint       Run ruff lint"
	@echo "  format     Apply ruff formatting"
	@echo "  typecheck  Run mypy (strict)"
	@echo "  test       Run the test suite"
	@echo "  cov        Run tests with coverage report"
	@echo "  check      Run lint + typecheck + tests"
	@echo "  build      Build sdist and wheel"
	@echo "  clean      Remove build/test artifacts"

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy

test:
	pytest -m "not integration"

cov:
	pytest --cov=naibu --cov-report=term-missing --cov-report=html

check: lint typecheck test

build:
	python -m build

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
