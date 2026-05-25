.PHONY: help setup lsp typecheck analyze validate clean

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
NPM ?= npm

help:
	@printf '%s\n' \
		'Available targets:' \
		'  make setup     Install Python dependencies' \
		'  make lsp       Install local language server tooling' \
		'  make typecheck Run Pyright against Python scripts' \
		'  make analyze   Regenerate analysis summaries from checked-in data' \
		'  make validate  Run the offline validation loop' \
		'  make clean     Remove local Python caches'

setup:
	$(PIP) install -r requirements.txt

lsp:
	$(NPM) install

typecheck:
	$(NPM) run typecheck

analyze:
	$(PYTHON) scripts/analyze_allosteric_challenge_datasets.py

validate:
	$(NPM) run typecheck
	$(PYTHON) scripts/analyze_allosteric_challenge_datasets.py
	git diff --check

clean:
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.ruff_cache' -o -name '.mypy_cache' \) -prune -exec rm -rf {} +
