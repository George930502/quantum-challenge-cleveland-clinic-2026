# AGENTS.md

## Scope

`data/` contains source artifacts downloaded from RCSB. Treat these files as immutable inputs unless the task is explicitly to refresh or add source data.

## Rules

- Do not manually edit `.pdb`, `.cif`, validation XML, FASTA, PDF gzip, or RCSB JSON files.
- Refresh data with `python3 -m scripts.pipeline.data_refresh.download_allosteric_challenge_rcsb`.
- Keep each PDB entry under `data/<dataset_slug>/rcsb/<pdb_id_lower>/`.
- Keep download manifests next to the downloaded artifacts.
- Prefer reading manifests and JSON metadata before opening large coordinate files.

## Verification

- After any data refresh, run `make validate`.
- Confirm changes are expected with `git diff --stat` before staging.
