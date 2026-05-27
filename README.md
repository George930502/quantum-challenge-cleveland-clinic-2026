# Quantum Challenge Cleveland Clinic 2026

Research workspace for the Cleveland Clinic 2026 quantum AI challenge around allosteric binding-site discovery. The repository keeps the raw RCSB inputs, derived structural summaries, and Traditional Chinese analysis notes together so the workflow can be reproduced by a coding agent or a human reviewer.

## Repository Map

- `data/` contains checked-in RCSB artifacts grouped by challenge dataset and PDB ID.
- `analysis/` contains generated per-dataset summaries, residue contact graphs, ligand-contact CSVs, and cross-dataset summaries.
- `docs/` contains grouped challenge notes, research synthesis documents, agent harness guidance, and review checklists.
- `scripts/` contains grouped executable scripts: `scripts/pipeline/` for scientific data workflows and `scripts/harness/` for repository-harness checks.

For a more detailed table of contents, see [docs/agent-harness/navigation/codebase-map.md](docs/agent-harness/navigation/codebase-map.md).

## Quick Start

```sh
python3 -m pip install -r requirements.txt
make lsp
make validate
```

`make validate` reruns the offline analysis from the checked-in `data/` directory and checks whitespace with `git diff --check`.
It also runs the harness documentation invariant check in `scripts/harness/check_harness_docs.py`.

## Language Server

The project uses Pyright as the Python LSP and type checker. Install the local language-server tooling with:

```sh
make lsp
```

Editors can use `node_modules/.bin/pyright-langserver --stdio`. VS Code users can open the workspace with the checked-in `.vscode/settings.json`.

## Data Workflow

1. Download or refresh RCSB artifacts:

   ```sh
   python3 -m scripts.pipeline.data_refresh.download_allosteric_challenge_rcsb
   ```

2. Regenerate the derived analysis:

   ```sh
   python3 -m scripts.pipeline.analysis.analyze_allosteric_challenge_datasets
   ```

3. Score current method runs against validation labels after prediction artifacts exist:

   ```sh
   make eval
   ```

4. Review changes in `analysis/` and `docs/` before committing. Treat validation structures and ligands as labels or sanity checks, not blind-feature inputs.

## Agent Workflow

Codex and other coding agents should start with [AGENTS.md](AGENTS.md), then read the nearest subdirectory `AGENTS.md` for scoped rules. The intended pattern is narrow context first, explicit verification, and small diffs that preserve scientific provenance.

Relevant docs:

- [docs/README.md](docs/README.md)
- [docs/agent-harness/navigation/codebase-map.md](docs/agent-harness/navigation/codebase-map.md)
- [docs/agent-harness/navigation/repository-structure-placement-guide.zh-TW.md](docs/agent-harness/navigation/repository-structure-placement-guide.zh-TW.md)
- [docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md](docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md)
- [docs/agent-harness/workflows/harness-operations-loop.zh-TW.md](docs/agent-harness/workflows/harness-operations-loop.zh-TW.md)
- [docs/agent-harness/research/deusyu-harness-engineering-alignment.zh-TW.md](docs/agent-harness/research/deusyu-harness-engineering-alignment.zh-TW.md)
- [docs/agent-harness/research/external-harness-resource-synthesis.zh-TW.md](docs/agent-harness/research/external-harness-resource-synthesis.zh-TW.md)
- [docs/agent-harness/state/challenge-harness-state.md](docs/agent-harness/state/challenge-harness-state.md)
- [docs/agent-harness/reviews/code-review-checklist.md](docs/agent-harness/reviews/code-review-checklist.md)
