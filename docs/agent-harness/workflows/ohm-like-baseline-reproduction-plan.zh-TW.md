# Ohm-Like Baseline Reproduction Plan

本文規劃 Wang et al. 2020 Ohm 方法在本 repo 的可重現實作流程。目標是先對齊原始論文描述與可取得程式碼，再把方法接到 Cleveland Clinic 2026 challenge 的 blind feature extraction、validation scoring、eval trace 流程。

## Source Inventory

| Item | Status | Evidence | Consequence |
| --- | --- | --- | --- |
| Paper | Available | Nature Communications article `10.1038/s41467-020-17618-2`; local literature note `docs/literature/classical-baselines/01-wang-2020-ohm.zh-TW.md`. | Use paper method as source of truth. |
| Official code | Not anonymously accessible as of 2026-05-25 | Paper code availability points to `https://bitbucket.org/dokhlab/ohm`; anonymous `git ls-remote https://bitbucket.org/dokhlab/ohm.git` required credentials and public HTTP check returned 404. | Treat as reproduction gap. If credentials or archive become available, inventory and prefer official code. |
| Local challenge data | Available | Checked-in RCSB artifacts under `data/`; generated summaries and contact labels under `analysis/`. | No network required for baseline MVP. |

## Paper-Method Alignment

| Paper requirement | Local implementation target | Provenance |
| --- | --- | --- |
| Structure-only input, no MD trajectory | Use checked-in challenge input structures only for feature construction. | Paper abstract/results; challenge harness leakage rule. |
| Atom-wise contact extraction | Compute heavy-atom residue-residue contacts from input PDB with 3.4 A cutoff. | Paper Methods, average atom-contacts matrix. |
| Propagation probability matrix | Current core runner converts atom contact counts with Wang et al. Eq. 3: `P_ij = 1 - exp(-alpha * C_ij / atom_count_i)`. Older `ohm_like_atom_contacts_strict_*` runs remain documented approximation baselines. | Paper Eq. 1-3 description; exact source code unavailable. |
| Active-site seeded allosteric-site prediction | Use permitted input active-site ligand contacts as perturbation seeds. | Paper active-site ACI workflow and seed-sensitivity discussion. |
| Repeated stochastic propagation | Use 10,000 rounds for primary runs, fixed RNG seed for repo determinism, and the paper's separate `V`/`W` vector traversal semantics. | Paper perturbation propagation algorithm; repo reproducibility rule. |
| ACI residue ranking | Rank residues by frequency of being affected by perturbation. | Paper ACI definition. |
| Hotspot clustering/pathway analysis | Hotspot clustering now uses seed-excluded 4.5 A direction-to-higher-ACI assignments. Pathway and critical-residue analysis remain open. | Paper hotspot method; active-site exclusion for allosteric-site reporting. |

## Resolved Challenge Policies

| Policy | Decision |
| --- | --- |
| Primary BCR-ABL1 strict run | Use `1OPL` chain A `P16` ATP-site contacts as active-site seed; exclude input `MYR` from primary benchmark. |
| BCR-ABL1 sensitivity run | Allow input `MYR` only in explicitly named sensitivity runs. |
| KRAS strict run | Use `4OBE` chain A `GDP` and `MG` contacts as active-site seed. |
| Seed cutoff | Use 5.0 A heavy-atom ligand-contact cutoff for primary seed residues; 8.0 A only as sensitivity. |
| Validation label cutoff | Keep validation ligand contact labels at 8.0 A for scoring. |
| Cardiac Myosin | Run exploratory outputs only until the validation-label caveat is resolved. |
| 8 A centroid graph | Use only as `centroid_graph_*` comparator, not as Ohm reproduction. |
| Probability formula while official code is unavailable | Current paper-aligned runs use Wang et al. Eq. 3: `P_ij = 1 - exp(-alpha * C_ij / atom_count_i)`, with paper default alpha 3.0. Older approximation runs use `P_ij = min(1, alpha * C_ij / atom_count_i)` and are labeled `official_code_unavailable_approximation`. |

## Implementation Checklist

1. Add an Ohm-like baseline runner under `scripts/pipeline/`.
2. Reuse existing PDB parsing and protein atom filtering patterns from `analyze_allosteric_challenge_datasets.py`.
3. Build atom-contact probability matrices from input structures only, using Wang et al. Eq. 3 for full reproduction.
4. Build active-site seed residues from allowed input ligand contacts and record excluded ligands/paths.
5. Emit deterministic outputs under `analysis/<dataset_slug>/runs/<run_id>/`:
   - connectivity matrix CSV;
   - residue hit list CSV;
   - hotspot summary CSV;
   - residue-hotspot assignment CSV;
   - method metadata JSON;
   - eval trace JSON.
6. Use the separate scorer script to read prediction outputs and validation contact labels only after prediction files exist.
7. Add smoke mode with 100 rounds for fast validation.
8. Add optional convergence comparison between 1,000 and 10,000 rounds after MVP.
9. Use `make eval` to score the current primary KRAS/BCR-ABL1 Ohm runs.
10. Run `make typecheck` and `make validate` after script and generated-output changes.

## Verification Matrix

| Check | Expected outcome |
| --- | --- |
| Paper alignment | Every method parameter in metadata has provenance: paper, repo decision, or explicit approximation. |
| Leakage guard | Prediction runner does not read validation structures, validation ligand-contact CSVs, or validation-derived labels. |
| Determinism | Repeating a run with the same random seed produces identical hit list and eval trace metrics. |
| Scoring separation | `scripts/pipeline/score_residue_hit_lists.py` runs after prediction generation and is the first stage allowed to read validation labels. |
| Benchmark scope | KRAS and BCR-ABL1 get strict scored runs; Cardiac Myosin is reported as exploratory unless validation is resolved. |

## Verification Status

As of 2026-05-27, the current runner aligns the core probability, propagation semantics, and hotspot clustering, but is not a full Ohm reproduction. The detailed audit is recorded in `docs/agent-harness/reviews/ohm-full-reproduction-verification-2026-05-27.zh-TW.md`.

## Open Gaps

- Official Bitbucket source is cited by the paper but currently not anonymously accessible from this environment.
- Exact Eq. 1-3 implementation details should be cross-checked against official code if it becomes available.
- Pathway critical-residue weighting, pairwise allosteric correlations, and paper benchmark reproduction are not yet implemented.
