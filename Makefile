PY ?= python
VENV ?= .venv

.PHONY: setup data train evaluate analytics run smoke test lint ci all

setup:
	$(PY) -m venv $(VENV)
	$(VENV)/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
	$(VENV)/bin/python -m pip install -e .

data:
	$(PY) -m scripts.clean_data

train:
	$(PY) -m scripts.train

evaluate:
	$(PY) -m scripts.evaluate

analytics:
	$(PY) -m scripts.build_analytics

run:
	flask --app webapp run

smoke:
	$(PY) -m pytest tests/smoke -m smoke

test:
	$(PY) -m pytest --cov --cov-report=term-missing --cov-fail-under=80

lint:
	ruff check .
	ruff format --check .

ci: lint test

all: data train evaluate analytics ci
