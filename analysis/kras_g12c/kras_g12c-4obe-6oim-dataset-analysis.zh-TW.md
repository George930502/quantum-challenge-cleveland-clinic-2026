# KRAS G12C Oncology 4OBE/6OIM 資料集分析報告

## 資料來源與任務定位

- Challenge objective: Identify the cryptic Switch-II pocket locked by Sotorasib / AMG 510.
- Input structure: `4OBE` (<https://www.rcsb.org/structure/4OBE>)
- Validation structure: `6OIM` (<https://www.rcsb.org/structure/6OIM>)
- Validation marker: AMG 510 / Sotorasib bound-form component MOV
- 資料風險：Low; 6OIM contains the MOV validation ligand, but MOV coordinates must only be used as validation labels, not blind input features.

Browser 自動化已核對 RCSB structure page 與 `Download Files` 選單；下載內容包含 PDB、mmCIF、FASTA、entry/entity/assembly JSON 與 validation 檔案。

## RCSB metadata 摘要

| PDB | Title | Method | Resolution (A) | Atoms | Polymer monomers | Release | DOI |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 4OBE | Crystal Structure of GDP-bound Human KRas | X-RAY DIFFRACTION | 1.24 | 3093 | 340 | 2014-06-04T00:00:00.000+00:00 | 10.1073/pnas.1404639111 |
| 6OIM | Crystal Structure of human KRAS G12C covalently bound to AMG 510 | X-RAY DIFFRACTION | 1.65 | 1613 | 183 | 2019-11-06T00:00:00.000+00:00 | 10.1038/s41586-019-1694-1 |

## 檔案與資料維度

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

## FASTA 與 mmCIF 維度

| PDB | FASTA records | FASTA lengths | mmCIF categories | mmCIF loops | atom_site rows |
| --- | ---: | --- | ---: | ---: | ---: |
| 4OBE | 1 | 170 | 75 | 42 | 5725 |
| 6OIM | 1 | 183 | 69 | 31 | 1613 |

## 鏈、殘基與 B-factor 維度

| PDB | Chain | Atoms | Residues | CA | Residue span | Missing numbers | Mean B-factor |
| --- | --- | ---: | ---: | ---: | --- | --- | ---: |
| 4OBE | A | 2648 | 169 | 169 | 1-169 | - | 18.458 |
| 4OBE | B | 2646 | 170 | 170 | 0-169 | - | 17.927 |
| 6OIM | A | 1336 | 167 | 167 | 0-169 | 105, 106, 107 | 24.312 |

## 配體與 heterogen 維度

| PDB | Component | Description | Instances | Heavy atoms | Chains | Likely signal ligand |
| --- | --- | --- | ---: | ---: | --- | --- |
| 4OBE | GDP | GUANOSINE-5'-DIPHOSPHATE | 2 | 56 | A, B |  |
| 4OBE | HOH |  | 355 | 355 | A, B |  |
| 4OBE | MG | MAGNESIUM ION | 2 | 2 | A, B |  |
| 6OIM | GDP | GUANOSINE-5'-DIPHOSPHATE | 1 | 28 | A |  |
| 6OIM | HOH |  | 207 | 207 | A |  |
| 6OIM | MG | MAGNESIUM ION | 1 | 1 | A |  |
| 6OIM | MOV | AMG 510 (bound form) | 1 | 41 | A | yes |

## Pair alignment 檢查

此段只使用 PDB residue numbering 的共同 CA 原子做快速 sanity check；若兩個 PDB 不是同一蛋白或 numbering schema 不一致，RMSD 只能當資料品質警訊，不能當嚴格結構疊合結論。

| Input chain | Validation chain | Common CA residues | RMSD (A) | Residue-name mismatch count |
| --- | --- | ---: | ---: | ---: |
| A | A | 166 | 1.362 | 4 |

## Validation ligand contact residues

| Threshold | Target validation contact residues |
| --- | ---: |
| <= 5 A | 22 |
| <= 6 A | 27 |
| <= 8 A | 49 |

| Ligand | Chain | Residue | Resname | Distance (A) |
| --- | --- | ---: | --- | ---: |
| MOV | A | 12 | CYS | 1.805 |
| MOV | A | 16 | LYS | 2.765 |
| MOV | A | 59 | ALA | 3.155 |
| MOV | A | 68 | ARG | 3.156 |
| MOV | A | 60 | GLY | 3.16 |
| MOV | A | 63 | GLU | 3.223 |
| MOV | A | 96 | TYR | 3.27 |
| MOV | A | 72 | MET | 3.277 |
| MOV | A | 103 | VAL | 3.36 |
| MOV | A | 9 | VAL | 3.447 |
| MOV | A | 34 | PRO | 3.482 |
| MOV | A | 10 | GLY | 3.497 |
| MOV | A | 99 | GLN | 3.507 |
| MOV | A | 61 | GLN | 3.516 |
| MOV | A | 95 | HIS | 3.551 |
| MOV | A | 62 | GLU | 3.628 |
| MOV | A | 58 | THR | 3.941 |
| MOV | A | 100 | ILE | 4.138 |
| MOV | A | 69 | ASP | 4.28 |
| MOV | A | 11 | ALA | 4.282 |
| MOV | A | 13 | GLY | 4.323 |
| MOV | A | 92 | ASP | 4.708 |
| MOV | A | 64 | TYR | 5.14 |
| MOV | A | 35 | THR | 5.339 |
| MOV | A | 37 | GLU | 5.622 |
| MOV | A | 78 | PHE | 5.745 |
| MOV | A | 97 | ARG | 5.904 |
| MOV | A | 8 | VAL | 6.169 |
| MOV | A | 7 | VAL | 6.25 |
| MOV | A | 14 | VAL | 6.318 |

完整 contact CSV：`analysis/kras_g12c/kras_g12c-validation-ligand-contact-residues-8a.csv`

## Residue contact graph 維度

| PDB | Selected chain | Nodes | Edges | Adjacency matrix | Avg degree | Max degree | Components |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 4OBE | A | 169 | 808 | 169 x 169 | 9.562 | 17 | 1 |
| 6OIM | A | 167 | 809 | 167 x 167 | 9.689 | 17 | 1 |

這些 graph dimensions 可作為後續 connectivity matrix 或 quantum walk/Hamiltonian simulation 的基礎維度。對多鏈或非同源 validation pair，建議先明確決定建模 chain 或 domain，再建立 challenge-specific coarse-graining。
