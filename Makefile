.PHONY: install test lint typecheck check demo build clean

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	ruff check .

typecheck:
	mypy src/memdevice_bench

check: lint typecheck test

demo:
	python scripts/generate_example.py

build: check
	python -m build
	python -m twine check dist/*

clean:
	rm -rf build dist .coverage htmlcov .pytest_cache .mypy_cache .ruff_cache
	rm -rf src/*.egg-info src/memdevice_bench/__pycache__ tests/__pycache__
	rm -rf examples/rram_2t_report examples/ecram_tft_3t_report
