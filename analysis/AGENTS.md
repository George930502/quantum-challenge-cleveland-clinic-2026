# AGENTS.md

## Scope

`analysis/` contains generated outputs from `scripts/analyze_allosteric_challenge_datasets.py` plus dataset-specific interpretation notes.

## Rules

- Regenerate machine-readable summaries and CSVs with `make analyze`.
- Keep per-dataset outputs in `analysis/<dataset_slug>/`.
- Keep cross-dataset summaries in `analysis/cross_dataset/`.
- Keep filenames stable because docs may reference them.
- For scientific interpretation changes, cite the derived summary or source artifact that supports the claim.

## Verification

- Run `make validate` after changing scripts or generated analysis.
- For note-only edits, run `git diff --check`.
