# Codebase Map

This map gives Codex and human reviewers a compact table of contents before opening larger files.

## Top-Level Directories

| Path | Purpose | Start With |
| --- | --- | --- |
| `data/` | Checked-in RCSB source artifacts grouped by dataset and PDB ID. | `data/AGENTS.md`, download manifests, entry JSON files. |
| `analysis/` | Generated summaries, residue contact graphs, ligand contacts, and dataset interpretation notes. | `analysis/AGENTS.md`, `analysis/cross_dataset/allosteric-challenge-three-dataset-cross-summary.json`. |
| `docs/` | Grouped challenge notes, cross-dataset synthesis, Codex harness guidance, task state, and review checklist. | `docs/AGENTS.md`, `docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md`, `docs/research/allosteric-challenge-three-dataset-feature-analysis.zh-TW.md`. |
| `scripts/` | Python downloader and offline analyzer. | `scripts/AGENTS.md`, `scripts/pipeline/analyze_allosteric_challenge_datasets.py`. |

## Dataset Slugs

| Slug | Domain | Input Structure | Validation Structure | Primary Question |
| --- | --- | --- | --- | --- |
| `kras_g12c` | Oncology | `4OBE` | `6OIM` | Identify the cryptic Switch-II pocket associated with AMG 510 / Sotorasib. |
| `bcr_abl1` | Oncology | `1OPL` | `5MO4` | Identify the distal myristoyl pocket used by Asciminib. |
| `cardiac_myosin` | Cardiology | `5TBY` | `6C1H` | Identify the mechanical regulatory site relevant to Mavacamten-like modulation. |

## Common Navigation Patterns

- To inspect data provenance, open `*_download_manifest.json` before opening coordinate files.
- To inspect dataset-level outputs, open `analysis/<dataset_slug>/<dataset_slug>-dataset-summary.json`.
- To inspect residue-neighborhood features, use `*-residue-contact-graph-8a.csv`.
- To inspect validation-ligand labels, use `*-validation-ligand-contact-residues-8a.csv`.
- To inspect human interpretation, read the per-dataset `.zh-TW.md` file and the cross-dataset doc in `docs/research/`.

## Documentation Layout

| Path | Purpose |
| --- | --- |
| `docs/challenge/` | Original challenge statement and competition-detail notes. |
| `docs/research/` | Research synthesis and generated cross-dataset reports. |
| `docs/agent-harness/` | Agent guidance, codebase map, challenge harness blueprint, durable task state, eval trace schema, and review checklist. |

## Harness Entrypoints

| Path | Use |
| --- | --- |
| `docs/agent-harness/README.md` | Index and placement rules for harness documentation. |
| `docs/agent-harness/navigation/repository-structure-placement-guide.zh-TW.md` | File placement and naming rules for future repo changes. |
| `docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md` | Challenge-specific harness architecture and work packages. |
| `docs/agent-harness/research/external-harness-resource-synthesis.zh-TW.md` | Synthesis of the external resources linked by `walkinglabs/awesome-harness-engineering`. |
| `docs/agent-harness/state/challenge-harness-state.md` | Durable working memory for long-running research tasks and handoffs. |
| `docs/agent-harness/schemas/eval-trace.schema.json` | Minimal schema for future method-run records and scoring traces. |
| `.codex/README.md` | Recommended Codex local environment actions. |

## Large Files

Coordinate and validation files can be noisy for agent context. Prefer targeted shell tools:

```sh
rg '^HETATM|^ATOM|^HEADER|^TITLE|^COMPND|^SOURCE' data/<dataset>/rcsb/<pdb>/<PDB>.pdb
```

Use Python or structured JSON parsing for reproducible analysis rather than manual coordinate edits.
