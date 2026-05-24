# BCR-ABL1 Oncology 1OPL/5MO4 資料集分析報告

## 資料來源與任務定位

- Challenge objective: Identify the distal myristoyl pocket used by Asciminib.
- Input structure: `1OPL` (<https://www.rcsb.org/structure/1OPL>)
- Validation structure: `5MO4` (<https://www.rcsb.org/structure/5MO4>)
- Validation marker: Asciminib / ABL001 candidate component AY7
- 資料風險：The validation structure also contains an ATP-site inhibitor, so allosteric-vs-orthosteric ligand labels must be kept separate.

Browser 自動化已核對 RCSB structure page 與 `Download Files` 選單；下載內容包含 PDB、mmCIF、FASTA、entry/entity/assembly JSON 與 validation 檔案。

## RCSB metadata 摘要

| PDB | Title | Method | Resolution (A) | Atoms | Polymer monomers | Release | DOI |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 1OPL | Structural basis for the auto-inhibition of c-Abl tyrosine kinase | X-RAY DIFFRACTION | 3.42 | 6655 | 1074 | 2003-04-08T00:00:00.000+00:00 | 10.1016/S0092-8674(03)00194-6 |
| 5MO4 | ABL1 kinase (T334I_D382N) in complex with asciminib and nilotinib | X-RAY DIFFRACTION | 2.17 | 3770 | 495 | 2017-04-05T00:00:00.000+00:00 | 10.1038/nature21702 |

## 檔案與資料維度

| PDB | Artifact | Path | Bytes | Lines / rows |
| --- | --- | --- | ---: | ---: |
| 1OPL | pdb | `data/bcr_abl1/rcsb/1opl/1OPL.pdb` | 616248 | 7608 |
| 1OPL | cif | `data/bcr_abl1/rcsb/1opl/1OPL.cif` | 730696 | 6655 |
| 1OPL | fasta | `data/bcr_abl1/rcsb/1opl/1OPL.fasta` | 617 | 2 |
| 1OPL | entry_json | `data/bcr_abl1/rcsb/1opl/1OPL_entry.json` | 14738 | 1 |
| 1OPL | validation_xml | `data/bcr_abl1/rcsb/1opl/1OPL_validation.xml` | 279190 | 1394 |
| 1OPL | manifest | `data/bcr_abl1/rcsb/1opl/1OPL_download_manifest.json` | 3839 | 122 |
| 5MO4 | pdb | `data/bcr_abl1/rcsb/5mo4/5MO4.pdb` | 355833 | 4393 |
| 5MO4 | cif | `data/bcr_abl1/rcsb/5mo4/5MO4.cif` | 460182 | 3770 |
| 5MO4 | fasta | `data/bcr_abl1/rcsb/5mo4/5MO4.fasta` | 561 | 2 |
| 5MO4 | entry_json | `data/bcr_abl1/rcsb/5mo4/5MO4_entry.json` | 13069 | 1 |
| 5MO4 | validation_xml | `data/bcr_abl1/rcsb/5mo4/5MO4_validation.xml` | 206196 | 844 |
| 5MO4 | manifest | `data/bcr_abl1/rcsb/5mo4/5MO4_download_manifest.json` | 3211 | 102 |

## 鏈、殘基與 B-factor 維度

| PDB | Chain | Atoms | Residues | CA | Residue span | Missing numbers | Mean B-factor |
| --- | --- | ---: | ---: | ---: | --- | --- | ---: |
| 1OPL | A | 3628 | 451 | 451 | 81-531 | - | 84.964 |
| 1OPL | B | 2954 | 365 | 365 | 140-518 | 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251 | 170.717 |
| 5MO4 | A | 3385 | 429 | 429 | 83-531 | 296, 297, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419 | 36.056 |

## 配體與 heterogen 維度

| PDB | Component | Description | Instances | Heavy atoms | Chains | Likely signal ligand |
| --- | --- | --- | ---: | ---: | --- | --- |
| 1OPL | MYR | MYRISTIC ACID | 1 | 15 | A | yes |
| 1OPL | P16 | 6-(2,6-DICHLOROPHENYL)-2-{[3-(HYDROXYMETHYL)PHENYL]AMINO}-8-METHYLPYRIDO[2,3-D]PYRIMIDIN-7(8H)-ONE | 2 | 58 | A, B | yes |
| 5MO4 | AY7 | asciminib | 1 | 31 | A | yes |
| 5MO4 | HOH |  | 307 | 307 | A |  |
| 5MO4 | NIL | Nilotinib | 1 | 39 | A | yes |

## Pair alignment 檢查

此段只使用 PDB residue numbering 的共同 CA 原子做快速 sanity check；若兩個 PDB 不是同一蛋白或 numbering schema 不一致，RMSD 只能當資料品質警訊，不能當嚴格結構疊合結論。

| Input chain | Validation chain | Common CA residues | RMSD (A) | Residue-name mismatch count |
| --- | --- | ---: | ---: | ---: |
| A | A | 429 | 0.98 | 1 |

## Validation ligand contact residues

| Ligand | Chain | Residue | Resname | Distance (A) |
| --- | --- | ---: | --- | ---: |
| AY7 | A | 481 | GLU | 2.821 |
| AY7 | A | 359 | LEU | 3.223 |
| AY7 | A | 448 | LEU | 3.266 |
| AY7 | A | 360 | LEU | 3.381 |
| AY7 | A | 453 | THR | 3.475 |
| AY7 | A | 452 | ALA | 3.524 |
| AY7 | A | 363 | ALA | 3.574 |
| AY7 | A | 451 | ILE | 3.611 |
| AY7 | A | 521 | ILE | 3.622 |
| AY7 | A | 512 | PHE | 3.628 |
| AY7 | A | 525 | VAL | 3.675 |
| AY7 | A | 356 | ALA | 3.679 |
| AY7 | A | 487 | VAL | 3.684 |
| AY7 | A | 484 | PRO | 3.734 |
| AY7 | A | 529 | LEU | 3.757 |
| AY7 | A | 351 | ARG | 3.787 |
| AY7 | A | 483 | CYS | 3.837 |
| AY7 | A | 454 | TYR | 3.865 |
| AY7 | A | 456 | MET | 4.201 |
| AY7 | A | 482 | GLY | 4.393 |
| AY7 | A | 480 | PRO | 4.688 |
| AY7 | A | 355 | ASN | 4.819 |
| AY7 | A | 491 | MET | 4.944 |
| AY7 | A | 449 | TRP | 5.353 |
| AY7 | A | 361 | TYR | 5.558 |
| AY7 | A | 447 | LEU | 5.895 |
| AY7 | A | 364 | THR | 5.914 |
| AY7 | A | 516 | PHE | 6.012 |
| AY7 | A | 357 | VAL | 6.041 |
| AY7 | A | 358 | VAL | 6.202 |

完整 contact CSV：`analysis/bcr_abl1/bcr_abl1-validation-ligand-contact-residues-8a.csv`

## Residue contact graph 維度

| PDB | Selected chain | Nodes | Edges | Adjacency matrix | Avg degree | Max degree | Components |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1OPL | A | 451 | 2166 | 451 x 451 | 9.605 | 17 | 1 |
| 5MO4 | A | 429 | 2062 | 429 x 429 | 9.613 | 17 | 1 |

這些 graph dimensions 可作為後續 connectivity matrix 或 quantum walk/Hamiltonian simulation 的基礎維度。對多鏈或非同源 validation pair，建議先明確決定建模 chain 或 domain，再建立 challenge-specific coarse-graining。
