# AGENTS.md

## Project Purpose

This repository supports the Cleveland Clinic 2026 quantum AI challenge research workflow for allosteric binding-site discovery. It contains checked-in RCSB source artifacts, derived structural analyses, and Traditional Chinese research notes.

## Start Here

- Read `README.md` for the human-facing workflow.
- Read `docs/agent-harness/CODEBASE_MAP.md` before broad exploration.
- Use the nearest nested `AGENTS.md` when working under `data/`, `analysis/`, `docs/`, or `scripts/`.
- Prefer `rg` and targeted file reads over scanning large structural files.

## Repository Layout

- `data/`: raw RCSB artifacts. Large `.pdb`, `.cif`, validation XML, PDF gzip, FASTA, and JSON files are source inputs.
- `analysis/`: generated summaries, residue contact graphs, ligand-contact CSVs, and dataset-specific analysis notes.
- `docs/`: challenge notes, synthesis docs, Codex harness guidance, and review checklists.
- `scripts/`: reproducible Python pipeline for downloading and analyzing data.

## Environment

- Python 3.9+ is expected.
- Install dependencies with `python3 -m pip install -r requirements.txt`.
- The offline analysis dependency is `numpy`.
- Install local LSP/type-check tooling with `make lsp`.
- Python language-server support uses project-local Pyright (`node_modules/.bin/pyright-langserver`).
- Network is only required for `scripts/download_allosteric_challenge_rcsb.py`.

## Commands

- Setup: `make setup`
- LSP tooling: `make lsp`
- Type check: `make typecheck`
- Offline validation: `make validate`
- Regenerate analysis only: `make analyze`
- Refresh RCSB data: `python3 scripts/download_allosteric_challenge_rcsb.py`

## Working Rules

- Do not treat validation ligands or validation structures as blind input features unless a document explicitly says the task is validation or sanity-checking.
- Preserve dataset slugs: `kras_g12c`, `bcr_abl1`, and `cardiac_myosin`.
- Keep generated outputs deterministic and encoded as UTF-8.
- Do not rewrite checked-in RCSB artifacts by hand. Use the downloader for refreshes.
- Avoid loading entire `.pdb`, `.cif`, `.xml`, `.pdf.gz`, or large CSV files into context unless the task requires exact source inspection.
- When adding a new dataset, update the dataset specs in both scripts and add scoped analysis output under `analysis/<dataset_slug>/`.

## Verification

- Before committing, run `make validate`.
- If changing downloader behavior, run the downloader only when network access is available and then run `make validate`.
- For documentation-only edits, at minimum run `git diff --check`.
- Review against `docs/agent-harness/code_review.md` before publishing.
