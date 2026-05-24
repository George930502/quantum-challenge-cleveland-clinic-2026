# Code Review Checklist

Use this checklist for local review, Codex `/review`, or GitHub review prompts.

## Scientific Correctness

- Validation ligands and validation structures are not accidentally used as blind input features.
- Dataset slugs, PDB IDs, chain IDs, and ligand component IDs match the documented challenge setup.
- Claims in prose are supported by generated summaries, source metadata, or cited external references.
- Cardiac myosin validation caveats remain explicit where relevant.

## Reproducibility

- `make validate` passes after code or generated-output changes.
- Generated files are deterministic and encoded as UTF-8.
- New dependencies are listed in `requirements.txt` and explained in `README.md`.
- Downloader changes preserve manifests and failure reporting.

## Agent Harness

- Root guidance stays lean enough to load every session.
- Specialized guidance lives near the relevant subtree in nested `AGENTS.md` files.
- Large raw data is referenced through maps, manifests, and targeted commands instead of copied into prompts.
- Review and verification commands are explicit.

## Git Hygiene

- The diff contains only the intended task scope.
- Generated cache files and local environment files are ignored.
- Commit messages describe the user-visible change, not implementation trivia.
