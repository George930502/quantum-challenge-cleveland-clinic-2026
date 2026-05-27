.PHONY: help setup lsp typecheck harness-check analyze eval ohm-suite validate install-hooks clean

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
NPM ?= npm

help:
	@printf '%s\n' \
		'Available targets:' \
		'  make setup     Install Python dependencies' \
		'  make lsp       Install local language server tooling' \
		'  make typecheck Run Pyright against Python scripts' \
		'  make harness-check Validate agent harness documentation invariants' \
		'  make analyze   Regenerate analysis summaries from checked-in data' \
		'  make eval      Score current method runs against validation labels' \
		'  make ohm-suite Run Ohm alpha/seed-cutoff sensitivity suite' \
		'  make validate  Run the offline validation loop' \
		'  make install-hooks Enable repo-local git hooks' \
		'  make clean     Remove local Python caches'

setup:
	$(PIP) install -r requirements.txt

lsp:
	$(NPM) install

typecheck:
	$(NPM) run typecheck

harness-check:
	$(PYTHON) scripts/harness/check_harness_docs.py

analyze:
	$(PYTHON) -m scripts.pipeline.analysis.analyze_allosteric_challenge_datasets

eval:
	$(PYTHON) -m scripts.pipeline.evaluation.score_residue_hit_lists

ohm-suite:
	$(PYTHON) -m scripts.pipeline.baselines.ohm.run_ohm_baseline_suite

validate:
	$(NPM) run typecheck
	$(PYTHON) scripts/harness/check_harness_docs.py
	$(PYTHON) -m scripts.pipeline.analysis.analyze_allosteric_challenge_datasets
	$(PYTHON) -m scripts.pipeline.evaluation.score_residue_hit_lists
	git diff --check

install-hooks:
	git config core.hooksPath .githooks

clean:
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.ruff_cache' -o -name '.mypy_cache' \) -prune -exec rm -rf {} +
