# Harness State

This file is durable working memory for long-running agent sessions. Keep it concise and update it when a task changes the research direction, validation status, or next handoff.

## Current Objective

Build a reproducible quantum or quantum-inspired allosteric-site discovery workflow for the Cleveland Clinic 2026 challenge, starting from checked-in apo RCSB structures and scoring against validation labels without leaking validation ligands into blind feature extraction.

## Active Datasets

| Slug | Input | Validation | Status | Key caveat |
| --- | --- | --- | --- | --- |
| `kras_g12c` | 4OBE chain A | 6OIM chain A | Baseline structural analysis generated. | MOV validation ligand is label-only. |
| `bcr_abl1` | 1OPL chain A | 5MO4 chain A | Baseline structural analysis generated. | AY7 allosteric label must be separated from ATP-site inhibitor NIL. |
| `cardiac_myosin` | 5TBY chain A | 6C1H chain P | Baseline structural analysis generated; validation caveat open. | 6C1H may be a structural proxy rather than Mavacamten holo validation. |

## Harness Decisions

- Default setup remains offline and deterministic.
- RCSB refresh is explicit and network-gated.
- Generated analysis outputs are regenerated through `make analyze` or `make validate`.
- Validation ligand contacts are allowed only in scoring, sanity-check, or report-generation stages.
- Method runs should emit compact eval records matching `docs/agent-harness/schemas/eval-trace.schema.json` once modeling scripts exist.

## Open Work Packages

| ID | Package | Status | Next action |
| --- | --- | --- | --- |
| WP-1 | Baseline graph metrics | Not started | Add deterministic classical baselines for random ranking, degree, closeness, betweenness, and diffusion. |
| WP-2 | Quantum-inspired propagation | Not started | Define Hamiltonian or quantum walk over residue contact graph and output connectivity matrix plus hit list. |
| WP-3 | Scoring harness | Not started | Add evaluator that consumes blind predictions and validation contact labels separately. |
| WP-4 | Cardiac myosin validation check | Open | Confirm whether 6C1H is accepted by challenge organizers as validation proxy. |
| WP-5 | Run trace writer | Not started | Create JSONL run records under method-specific analysis output once methods are added. |

## Known Risks

- Data leakage from holo ligand coordinates into feature extraction would invalidate blind prediction claims.
- Residue numbering can drift across chains and aligned structures; every output must preserve PDB chain and residue number.
- Cardiac myosin has a large structural mismatch and an unresolved validation-marker issue.
- Quantum hardware claims require explicit qubit/coarse-graining assumptions and noise robustness checks.

## Handoff Notes

- Start every broad task with `AGENTS.md` and `docs/agent-harness/navigation/codebase-map.md`.
- For docs-only edits, run `git diff --check`.
- For script, generated output, or harness behavior changes, run `make validate`.
- Update this file when a work package changes state or a major assumption is resolved.
