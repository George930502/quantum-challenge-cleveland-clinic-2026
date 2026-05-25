# Quantum Challenge Cleveland Clinic 2026

Research workspace for the Cleveland Clinic 2026 quantum AI challenge around allosteric binding-site discovery. The repository keeps the raw RCSB inputs, derived structural summaries, and Traditional Chinese analysis notes together so the workflow can be reproduced by a coding agent or a human reviewer.

## Repository Map

- `data/` contains checked-in RCSB artifacts grouped by challenge dataset and PDB ID.
- `analysis/` contains generated per-dataset summaries, residue contact graphs, ligand-contact CSVs, and cross-dataset summaries.
- `docs/` contains grouped challenge notes, research synthesis documents, agent harness guidance, and review checklists.
- `scripts/` contains the downloader and offline analysis pipeline.

For a more detailed table of contents, see [docs/agent-harness/CODEBASE_MAP.md](docs/agent-harness/CODEBASE_MAP.md).

## Quick Start

```sh
python3 -m pip install -r requirements.txt
make lsp
make validate
```

`make validate` reruns the offline analysis from the checked-in `data/` directory and checks whitespace with `git diff --check`.

## Language Server

The project uses Pyright as the Python LSP and type checker. Install the local language-server tooling with:

```sh
make lsp
```

Editors can use `node_modules/.bin/pyright-langserver --stdio`. VS Code users can open the workspace with the checked-in `.vscode/settings.json`.

## Data Workflow

1. Download or refresh RCSB artifacts:

   ```sh
   python3 scripts/download_allosteric_challenge_rcsb.py
   ```

2. Regenerate the derived analysis:

   ```sh
   python3 scripts/analyze_allosteric_challenge_datasets.py
   ```

3. Review changes in `analysis/` and `docs/` before committing. Treat validation structures and ligands as labels or sanity checks, not blind-feature inputs.

## Agent Workflow

Codex and other coding agents should start with [AGENTS.md](AGENTS.md), then read the nearest subdirectory `AGENTS.md` for scoped rules. The intended pattern is narrow context first, explicit verification, and small diffs that preserve scientific provenance.

Relevant docs:

- [docs/README.md](docs/README.md)
- [docs/agent-harness/CODEBASE_MAP.md](docs/agent-harness/CODEBASE_MAP.md)
- [docs/agent-harness/codex-large-project-harness.zh-TW.md](docs/agent-harness/codex-large-project-harness.zh-TW.md)
- [docs/agent-harness/code_review.md](docs/agent-harness/code_review.md)
