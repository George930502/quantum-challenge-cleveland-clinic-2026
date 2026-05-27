# AGENTS.md

## Scope

`scripts/pipeline/` contains reproducible scientific data pipeline modules grouped by responsibility.

## Directory Layout

- `data_refresh/`: network-gated source-data download and refresh scripts.
- `analysis/`: deterministic offline analysis generators.
- `baselines/`: blind prediction method runners, grouped by method.
- `evaluation/`: post-prediction scoring and validation-only evaluators.

## Rules

- Keep downloader and analyzer behavior deterministic except for explicit network refreshes.
- Keep dataset metadata centralized in the pipeline scripts until a shared package is introduced.
- Do not add agent-harness maintenance checks here; those belong in `scripts/harness/`.

## Verification

- Run `make typecheck` after script edits.
- Run `make validate` after analyzer or generated-output changes.
- If downloader behavior changes, run `python3 -m scripts.pipeline.data_refresh.download_allosteric_challenge_rcsb` only when network access is available, then run `make validate`.
