#!/usr/bin/env sh
set -eu

python -m ruff format --check .
python -m ruff check .
python -m mypy src tests
python -m pytest
