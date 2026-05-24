# AGENTS.md

## Scope

`scripts/` contains the reproducible pipeline for downloading RCSB artifacts and generating offline structural analysis.

## Rules

- Keep scripts executable with `python3` and avoid hidden notebook-only state.
- Prefer standard-library code unless a dependency is already listed in `requirements.txt`.
- If adding dependencies, update `requirements.txt` and `README.md`.
- Preserve deterministic output ordering and UTF-8 writes.
- Keep dataset metadata centralized and update both downloader and analyzer specs when adding or changing datasets.

## Verification

- Run `make validate` after script changes.
- If downloader behavior changes, run `python3 scripts/download_allosteric_challenge_rcsb.py` when network access is available, then run `make validate`.
