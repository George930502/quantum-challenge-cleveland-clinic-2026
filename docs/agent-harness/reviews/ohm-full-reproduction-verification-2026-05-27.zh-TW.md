# Ohm Full Reproduction Verification

日期：2026-05-27

範圍：比對 `docs/literature/classical-baselines/papers/01_wang_2020_ohm_mapping_allosteric_communications.pdf` 的完整 Ohm 方法，與目前 codespace 中 `scripts/pipeline/run_ohm_like_baseline.py` 及已產生的 KRAS/BCR-ABL1 run outputs。

## Verdict

目前 codespace **尚未 fully reproduce** Wang et al. 2020 Ohm 的完整方法。

2026-05-27 更新：`scripts/pipeline/run_ohm_like_baseline.py` 已完成核心 paper-alignment slices，將 probability formula 改為 Wang et al. Eq. 3、alpha primary default 改為 3.0，改用 separate `V`/`W` traversal semantics，並加入 4.5 A direction-to-higher-ACI hotspot clustering。`scripts/pipeline/score_residue_hit_lists.py` 已加入挑戰賽 validation-label scorer。新的 primary outputs 使用 `ohm_atom_contacts_strict_*_alpha3p0_*` run id。完整 paper reproduction 仍缺 pathway/critical-residue analysis、pairwise allosteric correlations 與 paper benchmark datasets。

## Paper Method Requirements

| Paper requirement | Paper source | Required for full reproduction |
| --- | --- | --- |
| Atom contact cutoff | Methods: atoms within 3.4 A are counted as contacts. | Contact extraction must use 3.4 A atom-wise contacts. |
| Sequence-adjacent backbone exclusion | Methods Eq. 1 text: atoms `a` and `b` cannot be backbone atoms simultaneously when `|i-j| = 1`. | Exclude only adjacent-residue backbone-backbone atom contacts. |
| Average atom contacts | Eq. 2: `Nij = Cij / Ci`, `Nji = Cij / Cj`. | Directed normalization by source residue atom count. |
| Propagation probability | Eq. 3: `Pij = 1 - exp(-alpha * Nij)`. | Use exponential conversion, not linear clipping. |
| Default alpha | Methods Eq. 3 text: alpha is currently set to 3.0. | Default primary reproduction should use alpha 3.0; alpha 1-5 is sensitivity. |
| Stochastic propagation | Methods: initialize V/W/T, mark active-site residues, visit neighbors, set `Wm = 1` regardless of successful propagation, repeat until all W are 1, then repeat `10^4` rounds. | Traversal must continue through visited neighbors even if current edge does not propagate conformational change. |
| Allosteric-site prediction | Methods: active-site residues excluded; highest non-active-site ACI selected as allosteric site. | Hit list should explicitly identify highest non-seed ACI residue/site. |
| Hotspot detection | Methods: residue-pair minimum atom distance, 4.5 A neighbor threshold, direction vector to a neighbor with higher ACI; `D=-1` centers are hotspots. | Full output must include hotspot centers and residue clusters. |
| Pathway and critical residues | Methods Eq. 4 and pathway histogram over `10^4` propagations when active/allosteric sites are known. | Full reproduction must record pathway histogram and critical-residue importance. |
| Unknown-site mode | Fig. 1/Results: allosteric correlations between residue pairs when active/allosteric sites are unknown. | Full method should include pairwise allosteric correlation mode. |
| Source code | Code availability: Ohm source cited at Bitbucket. | Prefer official code if access becomes available; otherwise mark exact source unavailable. |

## Current Code Alignment

| Area | Current implementation | Match? | Evidence |
| --- | --- | --- | --- |
| Input leakage boundary | Prediction runner records validation paths as excluded and uses input PDBs. | Match for challenge leakage policy, not a paper reproduction issue. | `validation_paths_for_metadata`; metadata `validation_paths_excluded_from_features`. |
| Contact cutoff | Default `3.4`. | Match. | `DEFAULT_ATOM_CONTACT_CUTOFF_A = 3.4`. |
| Backbone exclusion | Excludes contacts when residue numbers differ by 1 and both atom names are in `{N, CA, C, O, OXT}`. | Mostly match. | `is_sequence_adjacent_backbone_contact`. |
| Average atom contacts | Uses `contact_counts[row] / atom_count_i`. | Partial match. | `propagation_matrix`. |
| Probability formula | Uses `1 - exp(-alpha * Cij / atom_count_i)`. | Match for Eq. 3. | `method.formula_provenance: wang_2020_eq_3`. |
| Alpha default | Uses `3.0`. | Match. | New primary metadata `alpha: 3.0`. |
| Propagation traversal | Uses separate affected and visited vectors; failed propagation still marks candidates visited. | Match for the paper's described `V`/`W` semantics. | `method.traversal_provenance: wang_2020_v_w_vectors`. |
| Repetition count | Primary run uses `10,000`. | Match. | Primary metadata `rounds: 10000`. |
| Active-site exclusion in ranking | Seed residues are blanked in `rank_non_seed`. | Partial match. | Paper selects highest ACI among remaining residues; current hit list ranks all non-seed residues but does not emit a selected allosteric site object. |
| Hotspot clustering | Seed-excluded allosteric hotspot clustering uses 4.5 A minimum atom-distance neighbors and direction-to-higher-ACI assignment. | Match for the paper hotspot step, with explicit active-site exclusion for allosteric-site reporting. | `method.hotspot_provenance: wang_2020_4p5a_direction_to_higher_aci`; `hotspots.csv`; `residue-hotspot-assignments.csv`. |
| Pathways and critical residues | Not implemented. | **Missing**. | No path stack, histogram, or Eq. 4 importance output exists. |
| Pairwise allosteric correlations | Not implemented. | **Missing**. | Runner requires seed residues and errors without seed policy. |
| Paper benchmark reproduction | Not implemented. | **Missing**. | No 20-protein Amor dataset, Caspase-1, CheY, CHESCA, TPR/PPV reproduction scripts or results. |

## Output Audit

Current paper-aligned primary runs exist for:

- `analysis/kras_g12c/runs/ohm_atom_contacts_strict_primary_kras_g12c_10000r_alpha3p0_seedcutoff5p0a/`
- `analysis/bcr_abl1/runs/ohm_atom_contacts_strict_primary_bcr_abl1_10000r_alpha3p0_seedcutoff5p0a/`

Older approximation runs are retained for comparison:

- `analysis/kras_g12c/runs/ohm_like_atom_contacts_strict_primary_kras_g12c_10000r_seedcutoff5p0a/`
- `analysis/bcr_abl1/runs/ohm_like_atom_contacts_strict_primary_bcr_abl1_10000r_seedcutoff5p0a/`

The current outputs are deterministic challenge baseline artifacts, but they are not sufficient evidence of full paper reproduction because:

- no paper-reported benchmark metrics are reproduced;
- no pathway, critical-residue, or pairwise-correlation output exists.

Current challenge scoring snapshot:

- KRAS primary: residue top-10 validation-contact hits 4, AUROC 0.66850105, average precision 0.27342268.
- BCR-ABL1 primary: residue top-10 validation-contact hits 0, AUROC 0.51717448, average precision 0.10374819; hotspot top-5 covers 27 of 46 validation residues.

## Required Fix List For Full Reproduction

1. Add pathway histogram and Eq. 4 critical-residue importance for runs with known active/allosteric site pairs.
2. Add pairwise allosteric correlation mode for unknown active/allosteric site scenarios.
3. Add paper-benchmark reproduction fixtures or scripts for the 20 known allosteric proteins, plus Caspase-1/CheY checks where local data availability permits.
4. Re-check official Ohm source access before finalizing exact reproduction; if still inaccessible, document the gap and every inferred implementation detail.

## Current Status Label

Use this status until the fix list is complete:

`challenge_baseline_scored__paper_pathway_and_correlation_open`
