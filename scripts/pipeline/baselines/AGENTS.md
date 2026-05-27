# AGENTS.md

## Scope

`scripts/pipeline/baselines/` contains method runners that produce prediction artifacts.

## Rules

- Keep blind feature extraction separate from validation scoring.
- Emit deterministic metadata and eval traces for each run.
- Put method-specific runners in method-specific subdirectories.

## Verification

- Run `make typecheck` after runner edits.
- Run `make validate` after generated-output changes.
