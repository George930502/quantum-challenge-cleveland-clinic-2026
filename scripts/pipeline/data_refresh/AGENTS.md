# AGENTS.md

## Scope

`scripts/pipeline/data_refresh/` contains network-gated source-data refresh scripts.

## Rules

- Keep downloaded RCSB artifacts under `data/`.
- Do not hand-edit checked-in RCSB artifacts.
- Network use should stay explicit and documented.

## Verification

- If downloader behavior changes, run it only when network access is available, then run `make validate`.
