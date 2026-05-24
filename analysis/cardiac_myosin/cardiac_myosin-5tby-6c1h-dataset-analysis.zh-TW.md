# Cardiac Myosin Cardiology 5TBY/6C1H 資料集分析報告

## 資料來源與任務定位

- Challenge objective: Identify the mechanical site where Mavacamten stabilizes the super-relaxed state.
- Input structure: `5TBY` (<https://www.rcsb.org/structure/5TBY>)
- Validation structure: `6C1H` (<https://www.rcsb.org/structure/6C1H>)
- Validation marker: No Mavacamten-like validation ligand detected in 6C1H by PDB component ID/name.
- 資料風險：RCSB describes 6C1H as actin-bound myosin-IB cryo-EM, not a cardiac myosin Mavacamten holo complex; treat it as a structural validation proxy only after challenge-organizer confirmation.

Browser 自動化已核對 RCSB structure page 與 `Download Files` 選單；下載內容包含 PDB、mmCIF、FASTA、entry/entity/assembly JSON 與 validation 檔案。

## RCSB metadata 摘要

| PDB | Title | Method | Resolution (A) | Atoms | Polymer monomers | Release | DOI |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 5TBY | HUMAN BETA CARDIAC HEAVY MEROMYOSIN INTERACTING-HEADS MOTIF OBTAINED BY HOMOLOGY MODELING (USING SWISS-MODEL) OF HUMAN SEQUENCE FROM APHONOPELMA HOMOLOGY MODEL (PDB-3JBH), RIGIDLY FITTED TO HUMAN BETA-CARDIAC NEGATIVELY STAINED THICK FILAMENT 3D-RECONSTRUCTION (EMD-2240) | ELECTRON MICROSCOPY | 20.0 | 20357 | 4592 | 2017-06-07T00:00:00.000+00:00 | 10.7554/eLife.24634 |
| 6C1H | High-Resolution Cryo-EM Structures of Actin-bound Myosin States Reveal the Mechanism of Myosin Force Sensing | ELECTRON MICROSCOPY | 3.9 | 20966 | 2752 | 2018-01-31T00:00:00.000+00:00 | 10.1073/pnas.1718316115 |

## 檔案與資料維度

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

## FASTA 與 mmCIF 維度

| PDB | FASTA records | FASTA lengths | mmCIF categories | mmCIF loops | atom_site rows |
| --- | ---: | --- | ---: | ---: | ---: |
| 5TBY | 3 | 166, 195, 1935 | 78 | 44 | 20357 |
| 6C1H | 3 | 375, 729, 148 | 77 | 41 | 20966 |

## 鏈、殘基與 B-factor 維度

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

## 配體與 heterogen 維度

| PDB | Component | Description | Instances | Heavy atoms | Chains | Likely signal ligand |
| --- | --- | --- | ---: | ---: | --- | --- |
| 6C1H | ADP | ADENOSINE-5'-DIPHOSPHATE | 5 | 135 | A, B, C, D, E |  |
| 6C1H | MG | MAGNESIUM ION | 5 | 5 | A, B, C, D, E |  |

## Pair alignment 檢查

此段只使用 PDB residue numbering 的共同 CA 原子做快速 sanity check；若兩個 PDB 不是同一蛋白或 numbering schema 不一致，RMSD 只能當資料品質警訊，不能當嚴格結構疊合結論。

| Input chain | Validation chain | Common CA residues | RMSD (A) | Residue-name mismatch count |
| --- | --- | ---: | ---: | ---: |
| A | P | 729 | 34.002 | 682 |

## Validation ligand contact residues

| Threshold | Target validation contact residues |
| --- | ---: |
| <= 5 A | 0 |
| <= 6 A | 0 |
| <= 8 A | 0 |

未偵測到指定 challenge validation ligand 的 8 A contact residue；詳見資料風險說明。

完整 contact CSV：`not generated`

## Residue contact graph 維度

| PDB | Selected chain | Nodes | Edges | Adjacency matrix | Avg degree | Max degree | Components |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 5TBY | A | 954 | 4126 | 954 x 954 | 8.65 | 16 | 1 |
| 6C1H | P | 729 | 3532 | 729 x 729 | 9.69 | 16 | 1 |

這些 graph dimensions 可作為後續 connectivity matrix 或 quantum walk/Hamiltonian simulation 的基礎維度。對多鏈或非同源 validation pair，建議先明確決定建模 chain 或 domain，再建立 challenge-specific coarse-graining。
