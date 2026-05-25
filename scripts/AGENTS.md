# AGENTS.md

## Scope

`scripts/` contains executable repository scripts grouped by responsibility.

## Directory Layout

- `pipeline/`: reproducible scientific data pipeline entrypoints for RCSB refresh, offline analysis, and future method evaluation.
- `harness/`: fast repository maintenance checks for agent-harness structure and documentation invariants.

## Rules

- Keep scripts executable with `python3` and avoid hidden notebook-only state.
- Prefer standard-library code unless a dependency is already listed in `requirements.txt`.
- If adding dependencies, update `requirements.txt` and `README.md`.
- Python LSP/type-checking uses local Pyright; update `pyrightconfig.json` when script import paths or supported Python versions change.
- Preserve deterministic output ordering and UTF-8 writes.
- Keep dataset metadata centralized and update both downloader and analyzer specs when adding or changing datasets.
- Put new scripts in the most specific subdirectory; do not add new Python entrypoints directly under `scripts/`.

## Verification

- Run `make typecheck` and `make validate` after script changes.
- If downloader behavior changes, run `python3 scripts/pipeline/download_allosteric_challenge_rcsb.py` when network access is available, then run `make validate`.
