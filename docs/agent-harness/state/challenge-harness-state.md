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
- Ohm-like active-site-seeded baseline runs should use strict blind inputs by default: KRAS may use input GDP/MG active-site contacts; BCR-ABL1 may use input `P16` ATP-site contacts but must exclude input `MYR` from the primary benchmark because it overlaps the target myristoyl-pocket concept. `MYR` is allowed only in explicitly labeled sensitivity runs.
- Ohm-like reproduction should use atom-wise contacts as the primary method path, matching the paper's contact-probability construction. Existing 8 A residue-centroid contact graphs are allowed only as explicitly named comparator baselines.
- Current paper-aligned Ohm stochastic baseline outputs are fixed for reproducibility: atom contact cutoff 3.4 A, alpha 3.0, random seed 20260525, 10,000 rounds for primary runs, 100 rounds for smoke runs, and optional 1,000-vs-10,000 convergence comparison. This aligns core propagation and hotspot clustering, but is not yet a full Wang et al. 2020 Ohm reproduction.
- Active-site seeds for primary Ohm-like runs use input heavy-atom ligand contacts within 5.0 A. KRAS uses `4OBE` chain A residues near `GDP` or `MG`; BCR-ABL1 uses `1OPL` chain A residues near `P16`. An 8.0 A seed cutoff is allowed only as a labeled sensitivity run. Validation labels keep their separate 8.0 A scoring cutoff.
- Core Ohm propagation now uses Wang et al. Eq. 3: `P_ij = 1 - exp(-alpha * C_ij / atom_count_i)`, alpha 3.0, and separate `V`/`W` traversal semantics. Hotspot clustering uses 4.5 A minimum atom-distance neighbors, excludes active-site seeds for allosteric hotspot reporting, and assigns residues toward higher-ACI neighbors. Older `ohm_like_atom_contacts_strict_*` outputs remain approximation baselines for comparison.
- 2026-05-27 Ohm full-reproduction verification status: not fully reproduced; current code is `challenge_baseline_scored__paper_pathway_and_correlation_open`. See `docs/agent-harness/reviews/ohm-full-reproduction-verification-2026-05-27.zh-TW.md`.
- Current Ohm challenge scoring reads validation labels only after prediction artifacts exist. KRAS primary score: residue top-10 hits 4/10, AUROC 0.66850105, AP 0.27342268. BCR-ABL1 primary score: residue top-10 hits 0/10, AUROC 0.51717448, AP 0.10374819; hotspot top-5 covers 27/46 validation residues.
- 2026-05-27 `deusyu/harness-engineering` alignment: added direct upstream gap audit, Ralph-style operations loop, local pre-commit hook, GitHub Actions fallback, and eval-trace validation inside `make harness-check`.

## Open Work Packages

| ID | Package | Status | Next action |
| --- | --- | --- | --- |
| WP-1 | Baseline graph metrics | In progress | Core Ohm propagation, hotspot clustering, and KRAS/BCR challenge scoring are implemented; BCR residue-ranking weakness requires sensitivity runs or comparator baselines. |
| WP-2 | Quantum-inspired propagation | Not started | Define Hamiltonian or quantum walk over residue contact graph and output connectivity matrix plus hit list. |
| WP-3 | Scoring harness | In progress | Current scorer emits per-run score reports and score traces; next add aggregate cross-run summary and comparator baselines. |
| WP-4 | Cardiac myosin validation check | Open | Confirm whether 6C1H is accepted by challenge organizers as validation proxy. |
| WP-5 | Run trace writer | In progress | Prediction-stage eval trace JSON and scoring-stage score trace JSON are emitted per run; next decide whether to aggregate JSONL. |

## Known Risks

- Data leakage from holo ligand coordinates into feature extraction would invalidate blind prediction claims.
- Residue numbering can drift across chains and aligned structures; every output must preserve PDB chain and residue number.
- Cardiac myosin has a large structural mismatch and an unresolved validation-marker issue.
- Quantum hardware claims require explicit qubit/coarse-graining assumptions and noise robustness checks.

## Handoff Notes

- Start every broad task with `AGENTS.md` and `docs/agent-harness/navigation/codebase-map.md`.
- For docs-only edits, run `git diff --check`.
- For script, generated output, or harness behavior changes, run `make validate`.
- For local hook parity with CI, run `make install-hooks` once per clone.
- Update this file when a work package changes state or a major assumption is resolved.
- Current Ohm-like prediction outputs:
  - `analysis/kras_g12c/runs/ohm_atom_contacts_strict_primary_kras_g12c_10000r_alpha3p0_seedcutoff5p0a/`
  - `analysis/bcr_abl1/runs/ohm_atom_contacts_strict_primary_bcr_abl1_10000r_alpha3p0_seedcutoff5p0a/`
  - `analysis/kras_g12c/runs/ohm_like_atom_contacts_strict_primary_kras_g12c_10000r_seedcutoff5p0a/`
  - `analysis/bcr_abl1/runs/ohm_like_atom_contacts_strict_primary_bcr_abl1_10000r_seedcutoff5p0a/`
