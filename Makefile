.PHONY: help setup analyze validate clean

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

help:
	@printf '%s\n' \
		'Available targets:' \
		'  make setup     Install Python dependencies' \
		'  make analyze   Regenerate analysis summaries from checked-in data' \
		'  make validate  Run the offline validation loop' \
		'  make clean     Remove local Python caches'

setup:
	$(PIP) install -r requirements.txt

analyze:
	$(PYTHON) scripts/analyze_allosteric_challenge_datasets.py

validate:
	$(PYTHON) scripts/analyze_allosteric_challenge_datasets.py
	git diff --check

clean:
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.ruff_cache' -o -name '.mypy_cache' \) -prune -exec rm -rf {} +
