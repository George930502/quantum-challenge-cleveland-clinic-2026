# AGENTS.md

## Scope

`scripts/pipeline/analysis/` contains deterministic offline analysis generators.

## Rules

- Keep outputs under `analysis/` and `docs/research/`.
- Keep analysis reproducible from checked-in data.
- Do not read validation labels inside blind prediction runners; validation labels belong in evaluation scripts.

## Verification

- Run `make validate` after analyzer changes.
