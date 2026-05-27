# AGENTS.md

## Project Purpose

This repository supports the Cleveland Clinic 2026 quantum AI challenge research workflow for allosteric binding-site discovery. It contains checked-in RCSB source artifacts, derived structural analyses, and Traditional Chinese research notes.

## Start Here

- Read `README.md` for the human-facing workflow.
- Read `docs/agent-harness/navigation/codebase-map.md` before broad exploration.
- For challenge-method or long-running research tasks, read `docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md` and update `docs/agent-harness/state/challenge-harness-state.md` when task state changes.
- Use the nearest nested `AGENTS.md` when working under `data/`, `analysis/`, `docs/`, or `scripts/`.
- Prefer `rg` and targeted file reads over scanning large structural files.
- Follow `docs/agent-harness/navigation/repository-structure-placement-guide.zh-TW.md` when adding or moving files.

## Repository Layout

- `data/`: raw RCSB artifacts. Large `.pdb`, `.cif`, validation XML, PDF gzip, FASTA, and JSON files are source inputs.
- `analysis/`: generated summaries, residue contact graphs, ligand-contact CSVs, and dataset-specific analysis notes.
- `docs/`: challenge notes, synthesis docs, Codex harness guidance, and review checklists.
- `scripts/`: grouped Python entrypoints. Use `scripts/pipeline/` for scientific workflows and `scripts/harness/` for repository checks.

## Environment

- Python 3.9+ is expected.
- Install dependencies with `python3 -m pip install -r requirements.txt`.
- The offline analysis dependency is `numpy`.
- Install local LSP/type-check tooling with `make lsp`.
- Python language-server support uses project-local Pyright (`node_modules/.bin/pyright-langserver`).
- Network is only required for `python3 -m scripts.pipeline.data_refresh.download_allosteric_challenge_rcsb`.

## Commands

- Setup: `make setup`
- LSP tooling: `make lsp`
- Type check: `make typecheck`
- Harness invariant check: `make harness-check`
- Offline validation: `make validate`
- Score current method runs: `make eval`
- Regenerate analysis only: `make analyze`
- Refresh RCSB data: `python3 -m scripts.pipeline.data_refresh.download_allosteric_challenge_rcsb`

## Working Rules

- Do not treat validation ligands or validation structures as blind input features unless a document explicitly says the task is validation or sanity-checking.
- Preserve dataset slugs: `kras_g12c`, `bcr_abl1`, and `cardiac_myosin`.
- Keep generated outputs deterministic and encoded as UTF-8.
- Do not rewrite checked-in RCSB artifacts by hand. Use the downloader for refreshes.
- Avoid loading entire `.pdb`, `.cif`, `.xml`, `.pdf.gz`, or large CSV files into context unless the task requires exact source inspection.
- When adding a new dataset, update the dataset specs in both scripts and add scoped analysis output under `analysis/<dataset_slug>/`.
- For new prediction methods, keep blind feature extraction separate from validation scoring and emit run metadata compatible with `docs/agent-harness/schemas/eval-trace.schema.json` once a run writer exists.

## Verification

- Before committing, run `make validate`.
- If changing downloader behavior, run the downloader only when network access is available and then run `make validate`.
- For documentation-only edits, at minimum run `git diff --check`.
- Review against `docs/agent-harness/reviews/code-review-checklist.md` before publishing.

## Agent skills

### Issue tracker

Issues and PRDs are tracked in GitHub Issues for `George930502/quantum-challenge-cleveland-clinic-2026`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default five-label triage vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repo: use root `CONTEXT.md` for domain language and root `docs/adr/` for future ADRs. See `docs/agents/domain.md`.
