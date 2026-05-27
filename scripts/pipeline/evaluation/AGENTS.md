# AGENTS.md

## Scope

`scripts/pipeline/evaluation/` contains post-prediction scoring and validation-only evaluation scripts.

## Rules

- Validation labels may be read here, after prediction artifacts already exist.
- Keep scoring deterministic and emit traceable reports.
- Do not write prediction features from validation structures.

## Verification

- Run `make eval` after scorer edits.
- Run `make validate` before publishing.
