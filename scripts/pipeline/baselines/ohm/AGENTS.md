# AGENTS.md

## Scope

`scripts/pipeline/baselines/ohm/` contains Wang et al. 2020 Ohm-style propagation runners and sensitivity suites.

## Rules

- Preserve paper-aligned Ohm parameters in metadata.
- Keep validation labels out of prediction-stage feature extraction.
- Label non-primary sensitivity runs clearly in run IDs and summaries.

## Verification

- Run `make ohm-suite` after suite changes when generated sensitivity outputs should be refreshed.
- Run `make validate` before publishing.
