# AGENTS.md

## Scope

`analysis/` contains generated outputs from `python3 -m scripts.pipeline.analysis.analyze_allosteric_challenge_datasets`, method-run outputs from pipeline runners, plus dataset-specific interpretation notes.

## Rules

- Regenerate machine-readable summaries and CSVs with `make analyze`.
- Keep per-dataset outputs in `analysis/<dataset_slug>/`.
- Keep method-run outputs under `analysis/<dataset_slug>/runs/<run_id>/`.
- Keep cross-dataset summaries in `analysis/cross_dataset/`.
- Keep filenames stable because docs may reference them.
- Do not hand-edit method-run outputs; rerun the corresponding `python3 -m scripts.pipeline...` entrypoint.
- For scientific interpretation changes, cite the derived summary or source artifact that supports the claim.

## Verification

- Run `make validate` after changing scripts or generated analysis.
- For note-only edits, run `git diff --check`.
