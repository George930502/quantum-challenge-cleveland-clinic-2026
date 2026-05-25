# AGENTS.md

## Scope

`scripts/pipeline/` contains reproducible scientific data pipeline entrypoints.

## Rules

- Keep downloader and analyzer behavior deterministic except for explicit network refreshes.
- Keep dataset metadata centralized in the pipeline scripts until a shared package is introduced.
- Do not add agent-harness maintenance checks here; those belong in `scripts/harness/`.

## Verification

- Run `make typecheck` after script edits.
- Run `make validate` after analyzer or generated-output changes.
- If downloader behavior changes, run `python3 scripts/pipeline/download_allosteric_challenge_rcsb.py` only when network access is available, then run `make validate`.
