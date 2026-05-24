# Allosteric Challenge 三資料集特徵分析總覽

## 文件目的

這份文件是 repo 的資料集入口文件。它整合三個 challenge dataset 的下載來源、檔案維度、結構維度、配體標記、validation contact、residue contact graph，以及資料集之間的比較。

資料由 `scripts/download_allosteric_challenge_rcsb.py` 下載，並由 `scripts/analyze_allosteric_challenge_datasets.py` 產生分析輸出。

## Dataset Scope

本報告交叉檢查 Cleveland Clinic challenge 中三個 minimum target families：

- KRAS G12C (Oncology): `4OBE` -> `6OIM`
- BCR-ABL1 (Oncology): `1OPL` -> `5MO4`
- Cardiac Myosin (Cardiology): `5TBY` -> `6C1H`

所有新增資料均由 RCSB 官方頁面與 API 下載，並由本 repo 的 scripts 產生可重跑分析。

## Cross-Dataset Dimension Overview

| Dataset | Input | Validation | Input graph nodes | Validation graph nodes | Target / marker | Target contacts | Exploratory contacts | Pair check | Risk note |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| KRAS G12C Oncology | 4OBE | 6OIM | 169 | 167 | AMG 510 / Sotorasib bound-form component MOV | 49 | 49 | 166 CA, RMSD 1.362 A | Low; 6OIM contains the MOV validation ligand, but MOV coordinates must only be used as validation labels, not blind input features. |
| BCR-ABL1 Oncology | 1OPL | 5MO4 | 451 | 429 | Asciminib / ABL001 candidate component AY7 | 46 | 46 | 429 CA, RMSD 0.98 A | The validation structure also contains an ATP-site inhibitor, so allosteric-vs-orthosteric ligand labels must be kept separate. |
| Cardiac Myosin Cardiology | 5TBY | 6C1H | 954 | 729 | No Mavacamten-like validation ligand detected in 6C1H by PDB component ID/name. | 0 | 0 | 729 CA, RMSD 34.002 A | RCSB describes 6C1H as actin-bound myosin-IB cryo-EM, not a cardiac myosin Mavacamten holo complex; treat it as a structural validation proxy only after challenge-organizer confirmation. |

## Feature Coverage Checklist

| Dataset | RCSB files | Metadata | Chain dimensions | Ligands | Validation contacts | Contact graph | Pair comparison |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KRAS G12C Oncology | yes | yes | yes | yes | yes | yes | yes |
| BCR-ABL1 Oncology | yes | yes | yes | yes | yes | yes | yes |
| Cardiac Myosin Cardiology | yes | yes | yes | yes | risk/needs review | yes | yes |

## KRAS G12C Oncology 詳細分析

### 任務定位

- Input: `4OBE` (<https://www.rcsb.org/structure/4OBE>)
- Validation: `6OIM` (<https://www.rcsb.org/structure/6OIM>)
- Challenge objective: Identify the cryptic Switch-II pocket locked by Sotorasib / AMG 510.
- Validation marker: AMG 510 / Sotorasib bound-form component MOV
- Risk note: Low; 6OIM contains the MOV validation ligand, but MOV coordinates must only be used as validation labels, not blind input features.

### RCSB Metadata

| PDB | Title | Method | Resolution (A) | Atoms | Polymer monomers | Release | DOI |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 4OBE | Crystal Structure of GDP-bound Human KRas | X-RAY DIFFRACTION | 1.24 | 3093 | 340 | 2014-06-04T00:00:00.000+00:00 | 10.1073/pnas.1404639111 |
| 6OIM | Crystal Structure of human KRAS G12C covalently bound to AMG 510 | X-RAY DIFFRACTION | 1.65 | 1613 | 183 | 2019-11-06T00:00:00.000+00:00 | 10.1038/s41586-019-1694-1 |

### File Dimensions

| PDB | Artifact | Path | Bytes | Lines / rows |
| --- | --- | --- | ---: | ---: |
| 4OBE | pdb | `data/kras_g12c/rcsb/4obe/4OBE.pdb` | 750465 | 9265 |
| 4OBE | cif | `data/kras_g12c/rcsb/4obe/4OBE.cif` | 888328 | 5725 |
| 4OBE | fasta | `data/kras_g12c/rcsb/4obe/4OBE.fasta` | 223 | 2 |
| 4OBE | entry_json | `data/kras_g12c/rcsb/4obe/4OBE_entry.json` | 20489 | 1 |
| 4OBE | validation_xml | `data/kras_g12c/rcsb/4obe/4OBE_validation.xml` | 186253 | 754 |
| 4OBE | manifest | `data/kras_g12c/rcsb/4obe/4OBE_download_manifest.json` | 3534 | 112 |
| 6OIM | pdb | `data/kras_g12c/rcsb/6oim/6OIM.pdb` | 173016 | 2136 |
| 6OIM | cif | `data/kras_g12c/rcsb/6oim/6OIM.cif` | 255266 | 1613 |
| 6OIM | fasta | `data/kras_g12c/rcsb/6oim/6OIM.fasta` | 232 | 2 |
| 6OIM | entry_json | `data/kras_g12c/rcsb/6oim/6OIM_entry.json` | 20220 | 1 |
| 6OIM | validation_xml | `data/kras_g12c/rcsb/6oim/6OIM_validation.xml` | 103935 | 432 |
| 6OIM | manifest | `data/kras_g12c/rcsb/6oim/6OIM_download_manifest.json` | 3571 | 112 |

### FASTA And mmCIF Dimensions

| PDB | FASTA records | FASTA lengths | mmCIF categories | mmCIF loops | atom_site rows |
| --- | ---: | --- | ---: | ---: | ---: |
| 4OBE | 1 | 170 | 75 | 42 | 5725 |
| 6OIM | 1 | 183 | 69 | 31 | 1613 |

### Chain, Residue, And B-Factor Dimensions

| PDB | Chain | Atoms | Residues | CA | Residue span | Missing numbers | Mean B-factor |
| --- | --- | ---: | ---: | ---: | --- | --- | ---: |
| 4OBE | A | 2648 | 169 | 169 | 1-169 | - | 18.458 |
| 4OBE | B | 2646 | 170 | 170 | 0-169 | - | 17.927 |
| 6OIM | A | 1336 | 167 | 167 | 0-169 | 105, 106, 107 | 24.312 |

### Ligands And Heterogens

| PDB | Component | Description | Instances | Heavy atoms | Chains | Likely signal ligand |
| --- | --- | --- | ---: | ---: | --- | --- |
| 4OBE | GDP | GUANOSINE-5'-DIPHOSPHATE | 2 | 56 | A, B |  |
| 4OBE | HOH |  | 355 | 355 | A, B |  |
| 4OBE | MG | MAGNESIUM ION | 2 | 2 | A, B |  |
| 6OIM | GDP | GUANOSINE-5'-DIPHOSPHATE | 1 | 28 | A |  |
| 6OIM | HOH |  | 207 | 207 | A |  |
| 6OIM | MG | MAGNESIUM ION | 1 | 1 | A |  |
| 6OIM | MOV | AMG 510 (bound form) | 1 | 41 | A | yes |

### Validation Contact Counts

| Threshold | Target validation contact residues |
| --- | ---: |
| <= 5 A | 22 |
| <= 6 A | 27 |
| <= 8 A | 49 |

Contact CSV: `analysis/kras_g12c/kras_g12c-validation-ligand-contact-residues-8a.csv`

### Residue Contact Graph Dimensions

| PDB | Selected chain | Nodes | Edges | Adjacency matrix | Avg degree | Max degree | Components |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 4OBE | A | 169 | 808 | 169 x 169 | 9.562 | 17 | 1 |
| 6OIM | A | 167 | 809 | 167 x 167 | 9.689 | 17 | 1 |


## BCR-ABL1 Oncology 詳細分析

### 任務定位

- Input: `1OPL` (<https://www.rcsb.org/structure/1OPL>)
- Validation: `5MO4` (<https://www.rcsb.org/structure/5MO4>)
- Challenge objective: Identify the distal myristoyl pocket used by Asciminib.
- Validation marker: Asciminib / ABL001 candidate component AY7
- Risk note: The validation structure also contains an ATP-site inhibitor, so allosteric-vs-orthosteric ligand labels must be kept separate.

### RCSB Metadata

| PDB | Title | Method | Resolution (A) | Atoms | Polymer monomers | Release | DOI |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 1OPL | Structural basis for the auto-inhibition of c-Abl tyrosine kinase | X-RAY DIFFRACTION | 3.42 | 6655 | 1074 | 2003-04-08T00:00:00.000+00:00 | 10.1016/S0092-8674(03)00194-6 |
| 5MO4 | ABL1 kinase (T334I_D382N) in complex with asciminib and nilotinib | X-RAY DIFFRACTION | 2.17 | 3770 | 495 | 2017-04-05T00:00:00.000+00:00 | 10.1038/nature21702 |

### File Dimensions

| PDB | Artifact | Path | Bytes | Lines / rows |
| --- | --- | --- | ---: | ---: |
| 1OPL | pdb | `data/bcr_abl1/rcsb/1opl/1OPL.pdb` | 616248 | 7608 |
| 1OPL | cif | `data/bcr_abl1/rcsb/1opl/1OPL.cif` | 730696 | 6655 |
| 1OPL | fasta | `data/bcr_abl1/rcsb/1opl/1OPL.fasta` | 617 | 2 |
| 1OPL | entry_json | `data/bcr_abl1/rcsb/1opl/1OPL_entry.json` | 14738 | 1 |
| 1OPL | validation_xml | `data/bcr_abl1/rcsb/1opl/1OPL_validation.xml` | 279190 | 1394 |
| 1OPL | manifest | `data/bcr_abl1/rcsb/1opl/1OPL_download_manifest.json` | 3841 | 122 |
| 5MO4 | pdb | `data/bcr_abl1/rcsb/5mo4/5MO4.pdb` | 355833 | 4393 |
| 5MO4 | cif | `data/bcr_abl1/rcsb/5mo4/5MO4.cif` | 460182 | 3770 |
| 5MO4 | fasta | `data/bcr_abl1/rcsb/5mo4/5MO4.fasta` | 561 | 2 |
| 5MO4 | entry_json | `data/bcr_abl1/rcsb/5mo4/5MO4_entry.json` | 13069 | 1 |
| 5MO4 | validation_xml | `data/bcr_abl1/rcsb/5mo4/5MO4_validation.xml` | 206196 | 844 |
| 5MO4 | manifest | `data/bcr_abl1/rcsb/5mo4/5MO4_download_manifest.json` | 3211 | 102 |

### FASTA And mmCIF Dimensions

| PDB | FASTA records | FASTA lengths | mmCIF categories | mmCIF loops | atom_site rows |
| --- | ---: | --- | ---: | ---: | ---: |
| 1OPL | 1 | 537 | 71 | 41 | 6655 |
| 5MO4 | 1 | 495 | 68 | 31 | 3770 |

### Chain, Residue, And B-Factor Dimensions

| PDB | Chain | Atoms | Residues | CA | Residue span | Missing numbers | Mean B-factor |
| --- | --- | ---: | ---: | ---: | --- | --- | ---: |
| 1OPL | A | 3628 | 451 | 451 | 81-531 | - | 84.964 |
| 1OPL | B | 2954 | 365 | 365 | 140-518 | 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251 | 170.717 |
| 5MO4 | A | 3385 | 429 | 429 | 83-531 | 296, 297, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419 | 36.056 |

### Ligands And Heterogens

| PDB | Component | Description | Instances | Heavy atoms | Chains | Likely signal ligand |
| --- | --- | --- | ---: | ---: | --- | --- |
| 1OPL | MYR | MYRISTIC ACID | 1 | 15 | A | yes |
| 1OPL | P16 | 6-(2,6-DICHLOROPHENYL)-2-{[3-(HYDROXYMETHYL)PHENYL]AMINO}-8-METHYLPYRIDO[2,3-D]PYRIMIDIN-7(8H)-ONE | 2 | 58 | A, B | yes |
| 5MO4 | AY7 | asciminib | 1 | 31 | A | yes |
| 5MO4 | HOH |  | 307 | 307 | A |  |
| 5MO4 | NIL | Nilotinib | 1 | 39 | A | yes |

### Validation Contact Counts

| Threshold | Target validation contact residues |
| --- | ---: |
| <= 5 A | 23 |
| <= 6 A | 27 |
| <= 8 A | 46 |

Contact CSV: `analysis/bcr_abl1/bcr_abl1-validation-ligand-contact-residues-8a.csv`

### Residue Contact Graph Dimensions

| PDB | Selected chain | Nodes | Edges | Adjacency matrix | Avg degree | Max degree | Components |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1OPL | A | 451 | 2166 | 451 x 451 | 9.605 | 17 | 1 |
| 5MO4 | A | 429 | 2062 | 429 x 429 | 9.613 | 17 | 1 |


## Cardiac Myosin Cardiology 詳細分析

### 任務定位

- Input: `5TBY` (<https://www.rcsb.org/structure/5TBY>)
- Validation: `6C1H` (<https://www.rcsb.org/structure/6C1H>)
- Challenge objective: Identify the mechanical site where Mavacamten stabilizes the super-relaxed state.
- Validation marker: No Mavacamten-like validation ligand detected in 6C1H by PDB component ID/name.
- Risk note: RCSB describes 6C1H as actin-bound myosin-IB cryo-EM, not a cardiac myosin Mavacamten holo complex; treat it as a structural validation proxy only after challenge-organizer confirmation.

### RCSB Metadata

| PDB | Title | Method | Resolution (A) | Atoms | Polymer monomers | Release | DOI |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 5TBY | HUMAN BETA CARDIAC HEAVY MEROMYOSIN INTERACTING-HEADS MOTIF OBTAINED BY HOMOLOGY MODELING (USING SWISS-MODEL) OF HUMAN SEQUENCE FROM APHONOPELMA HOMOLOGY MODEL (PDB-3JBH), RIGIDLY FITTED TO HUMAN BETA-CARDIAC NEGATIVELY STAINED THICK FILAMENT 3D-RECONSTRUCTION (EMD-2240) | ELECTRON MICROSCOPY | 20.0 | 20357 | 4592 | 2017-06-07T00:00:00.000+00:00 | 10.7554/eLife.24634 |
| 6C1H | High-Resolution Cryo-EM Structures of Actin-bound Myosin States Reveal the Mechanism of Myosin Force Sensing | ELECTRON MICROSCOPY | 3.9 | 20966 | 2752 | 2018-01-31T00:00:00.000+00:00 | 10.1073/pnas.1718316115 |

### File Dimensions

| PDB | Artifact | Path | Bytes | Lines / rows |
| --- | --- | --- | ---: | ---: |
| 5TBY | pdb | `data/cardiac_myosin/rcsb/5tby/5TBY.pdb` | 1919052 | 23692 |
| 5TBY | cif | `data/cardiac_myosin/rcsb/5tby/5TBY.cif` | 2201773 | 20357 |
| 5TBY | fasta | `data/cardiac_myosin/rcsb/5tby/5TBY.fasta` | 2517 | 6 |
| 5TBY | entry_json | `data/cardiac_myosin/rcsb/5tby/5TBY_entry.json` | 24357 | 1 |
| 5TBY | validation_xml | `data/cardiac_myosin/rcsb/5tby/5TBY_validation.xml` | 906984 | 8877 |
| 5TBY | manifest | `data/cardiac_myosin/rcsb/5tby/5TBY_download_manifest.json` | 3254 | 102 |
| 6C1H | pdb | `data/cardiac_myosin/rcsb/6c1h/6C1H.pdb` | 1799172 | 22212 |
| 6C1H | cif | `data/cardiac_myosin/rcsb/6c1h/6C1H.cif` | 2259872 | 20966 |
| 6C1H | fasta | `data/cardiac_myosin/rcsb/6c1h/6C1H.fasta` | 1473 | 6 |
| 6C1H | entry_json | `data/cardiac_myosin/rcsb/6c1h/6C1H_entry.json` | 13535 | 1 |
| 6C1H | validation_xml | `data/cardiac_myosin/rcsb/6c1h/6C1H_validation.xml` | 784444 | 6226 |
| 6C1H | manifest | `data/cardiac_myosin/rcsb/6c1h/6C1H_download_manifest.json` | 3964 | 122 |

### FASTA And mmCIF Dimensions

| PDB | FASTA records | FASTA lengths | mmCIF categories | mmCIF loops | atom_site rows |
| --- | ---: | --- | ---: | ---: | ---: |
| 5TBY | 3 | 166, 195, 1935 | 78 | 44 | 20357 |
| 6C1H | 3 | 375, 729, 148 | 77 | 41 | 20966 |

### Chain, Residue, And B-Factor Dimensions

| PDB | Chain | Atoms | Residues | CA | Residue span | Missing numbers | Mean B-factor |
| --- | --- | ---: | ---: | ---: | --- | --- | ---: |
| 5TBY | A | 7704 | 954 | 954 | 6-959 | - | 2.33 |
| 5TBY | B | 7673 | 950 | 950 | 10-959 | - | 2.248 |
| 5TBY | C | 1212 | 152 | 152 | 44-195 | - | 2.662 |
| 5TBY | D | 1212 | 152 | 152 | 44-195 | - | 2.818 |
| 5TBY | E | 1278 | 160 | 160 | 7-166 | - | 3.031 |
| 5TBY | F | 1278 | 160 | 160 | 7-166 | - | 3.19 |
| 6C1H | A | 2933 | 375 | 375 | 1-375 | - | 84.05 |
| 6C1H | B | 2933 | 375 | 375 | 1-375 | - | 70.569 |
| 6C1H | C | 2933 | 375 | 375 | 1-375 | - | 78.273 |
| 6C1H | D | 2933 | 375 | 375 | 1-375 | - | 99.227 |
| 6C1H | E | 2933 | 375 | 375 | 1-375 | - | 121.024 |
| 6C1H | P | 5570 | 729 | 729 | 6-734 | - | 120.877 |
| 6C1H | R | 591 | 148 | 148 | 1-148 | - | 150.239 |

### Ligands And Heterogens

| PDB | Component | Description | Instances | Heavy atoms | Chains | Likely signal ligand |
| --- | --- | --- | ---: | ---: | --- | --- |
| 6C1H | ADP | ADENOSINE-5'-DIPHOSPHATE | 5 | 135 | A, B, C, D, E |  |
| 6C1H | MG | MAGNESIUM ION | 5 | 5 | A, B, C, D, E |  |

### Validation Contact Counts

| Threshold | Target validation contact residues |
| --- | ---: |
| <= 5 A | 0 |
| <= 6 A | 0 |
| <= 8 A | 0 |

Contact CSV: `not generated`

### Residue Contact Graph Dimensions

| PDB | Selected chain | Nodes | Edges | Adjacency matrix | Avg degree | Max degree | Components |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 5TBY | A | 954 | 4126 | 954 x 954 | 8.65 | 16 | 1 |
| 6C1H | P | 729 | 3532 | 729 x 729 | 9.69 | 16 | 1 |



## Cross-Dataset Interpretation

1. KRAS G12C 是三者中最乾淨的 apo/holo validation pair：`6OIM` 明確包含 AMG 510 bound-form ligand `MOV`，可直接形成 residue-level ground truth。
2. BCR-ABL1 的 `5MO4` 包含 Asciminib candidate ligand marker `AY7`，但同時也有其他 kinase inhibitor/heterogen；後續模型必須把 myristoyl-pocket allosteric marker 與 ATP-site inhibitor 分開。
3. Cardiac Myosin 的 PDF challenge label 與 `6C1H` RCSB metadata 存在明顯語義落差：`6C1H` 是 actin-bound myosin-IB cryo-EM structure，且未偵測到 Mavacamten-like ligand。這一組可以先做 structural/mechanical proxy 分析，但提交前應向 challenge organizer 確認 validation label。
4. Contact graph node counts 差異很大，代表 coarse-graining 策略不能一體套用：KRAS 是百級 residue graph，BCR-ABL1 是 kinase/regulatory domain 中型 graph，Myosin 是大型 multi-chain motor/actin complex。

## Modeling Notes

- 先為每組資料明確定義「可用於 blind input 的 features」與「只能用於 validation 的 labels」。
- 對 BCR-ABL1 與 Myosin 這類多 domain 或跨蛋白資料，優先建立 domain-level chain selection 與 residue numbering 對應表。
- 對 Cardiac Myosin，先不要把 `6C1H` 當作 Mavacamten holo ground truth；可暫時作為 mechanical state comparison target。

## Summary

- `data/` 內的三組資料集目前都由同一支下載腳本產生；統一 manifest 是 `data/allosteric_challenge_rcsb_download_summary.json`。
- `analysis/` 內的 dataset summaries、contact graph CSV、contact residue CSV 都由同一支分析腳本產生。
- KRAS G12C 和 BCR-ABL1 具有明確 small-molecule validation marker，可直接用於 residue-level label 檢查。
- Cardiac Myosin 目前有完整結構維度與 graph 維度，但缺少 Mavacamten-like ligand marker；這是資料集使用前最重要的風險。
- 後續量子模型若要跨三組資料比較，應先統一 coarse-graining policy，再分別處理各資料集的 target-label 定義。
