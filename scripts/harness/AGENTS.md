# AGENTS.md

## Scope

`scripts/harness/` contains repository maintenance checks that make the agent harness mechanically verifiable.

## Rules

- Keep checks fast, offline, deterministic, and readable to agents.
- Prefer validating structure, required files, schemas, and internal links over broad content policing.
- Do not place scientific data pipeline behavior here; use `scripts/pipeline/`.

## Verification

- Run `make harness-check` after harness documentation or check-script edits.
- Run `make validate` before publishing structural changes.
