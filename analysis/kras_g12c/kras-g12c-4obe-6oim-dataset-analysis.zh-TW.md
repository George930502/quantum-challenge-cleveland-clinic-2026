# KRAS G12C Oncology 4OBE/6OIM 資料集分析報告

## 資料來源與網站核對

本報告分析 Cleveland Clinic Global Quantum + AI Challenge 2026 中 KRAS G12C (Oncology) 的 benchmark pair。PDF 表格中的 PDB ID 是 `4OBE` 與 `6OIM`；使用 Browser 自動化開啟 RCSB 頁面後確認：

- `4OBE`: <https://www.rcsb.org/structure/4OBE>
- `6OIM`: <https://www.rcsb.org/structure/6OIM>
- 兩個頁面的 `Download Files` 選單包含 FASTA、PDBx/mmCIF、Legacy PDB、PDBML/XML、validation 與 biological assembly 下載項目。

下載腳本：`scripts/download_kras_g12c_rcsb.py`
分析腳本：`scripts/analyze_kras_g12c_dataset.py`

## RCSB metadata 摘要

| PDB | Title | Method | Resolution (A) | Atoms | Polymer monomers | Release | DOI |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 4OBE | Crystal Structure of GDP-bound Human KRas | X-RAY DIFFRACTION | 1.24 | 3093 | 340 | 2014-06-04T00:00:00.000+00:00 | 10.1073/pnas.1404639111 |
| 6OIM | Crystal Structure of human KRAS G12C covalently bound to AMG 510 | X-RAY DIFFRACTION | 1.65 | 1613 | 183 | 2019-11-06T00:00:00.000+00:00 | 10.1038/s41586-019-1694-1 |

重要解讀：

- `4OBE` 是挑戰指定的輸入結構，RCSB title 為 GDP-bound Human KRas。它不是 G12C holo inhibitor complex；在 chain A 的第 12 位為 GLY。
- `6OIM` 是驗證結構，title 顯示 human KRAS G12C covalently bound to AMG 510。PDB 中 AMG 510 的 bound-form component ID 為 `MOV`。
- chain A residue comparison 顯示主要挑戰相關突變差異為：12:GLY->CYS, 51:CYS->SER, 80:CYS->LEU, 118:CYS->SER。

## 檔案與資料維度

| PDB | Artifact | Path | Bytes | Lines / rows |
| --- | --- | --- | ---: | ---: |
| 4OBE | pdb | `data/kras_g12c/rcsb/4obe/4OBE.pdb` | 750465 | 9265 |
| 4OBE | cif | `data/kras_g12c/rcsb/4obe/4OBE.cif` | 888328 | 5725 |
| 4OBE | fasta | `data/kras_g12c/rcsb/4obe/4OBE.fasta` | 223 | 2 |
| 4OBE | entry_json | `data/kras_g12c/rcsb/4obe/4OBE_entry.json` | 20489 | 1 |
| 4OBE | validation_xml | `data/kras_g12c/rcsb/4obe/4OBE_validation.xml` | 186253 | 754 |
| 4OBE | manifest | `data/kras_g12c/rcsb/4obe/4OBE_download_manifest.json` | 3529 | 112 |
| 6OIM | pdb | `data/kras_g12c/rcsb/6oim/6OIM.pdb` | 173016 | 2136 |
| 6OIM | cif | `data/kras_g12c/rcsb/6oim/6OIM.cif` | 255266 | 1613 |
| 6OIM | fasta | `data/kras_g12c/rcsb/6oim/6OIM.fasta` | 232 | 2 |
| 6OIM | entry_json | `data/kras_g12c/rcsb/6oim/6OIM_entry.json` | 20220 | 1 |
| 6OIM | validation_xml | `data/kras_g12c/rcsb/6oim/6OIM_validation.xml` | 103935 | 432 |
| 6OIM | manifest | `data/kras_g12c/rcsb/6oim/6OIM_download_manifest.json` | 3563 | 112 |

mmCIF 維度補充：

- `4OBE`: 75 個 mmCIF category、42 個 loop、atom_site rows = 5725。
- `6OIM`: 69 個 mmCIF category、31 個 loop、atom_site rows = 1613。

## 鏈與殘基維度

| PDB | Chain | Atoms | Residues | CA count | Residue span | Missing numbers inside span | Mean B-factor |
| --- | --- | ---: | ---: | ---: | --- | --- | ---: |
| 4OBE | A | 2648 | 169 | 169 | 1-169 | - | 18.458 |
| 4OBE | B | 2646 | 170 | 170 | 0-169 | - | 17.927 |
| 6OIM | A | 1336 | 167 | 167 | 0-169 | 105, 106, 107 | 24.312 |

對後續建模而言，chain A 是最直接的比較對象。若建立殘基接觸圖，可把每個 modeled residue 視為一個節點；本分析使用 residue centroid 距離小於等於 8 A 作為無向邊。

## 配體與 heterogen

| PDB | Component | Instances | Heavy atoms | Chains | Interpretation |
| --- | --- | ---: | ---: | --- | --- |
| 4OBE | GDP | 2 | 56 | A, B | nucleotide ligand / active-site reference |
| 4OBE | HOH | 355 | 355 | A, B |  |
| 4OBE | MG | 2 | 2 | A, B | magnesium ion |
| 6OIM | GDP | 1 | 28 | A | nucleotide ligand / active-site reference |
| 6OIM | HOH | 207 | 207 | A |  |
| 6OIM | MG | 1 | 1 | A | magnesium ion |
| 6OIM | MOV | 1 | 41 | A | AMG 510/Sotorasib bound-form ligand; validation allosteric pocket marker |

對本競賽的意義：

- GDP/MG 代表 nucleotide active-site 的幾何參考。
- `6OIM` 的 `MOV` 是 AMG 510/Sotorasib 的 bound form，可當作 Switch-II pocket 的 validation marker。
- `4OBE` 沒有 `MOV`，因此適合作為 blind input；演算法應從 apo/GDP-bound topology 預測 6OIM 中會被 AMG 510 佔據的異位口袋。

## 4OBE 對 6OIM 結構對齊

本分析以 chain A 的 common C-alpha residues 做 Kabsch alignment，使用 166 個共同 CA 原子。

| Region | RMSD (A) |
| --- | ---: |
| Global chain A | 1.362 |
| P-loop / nucleotide active site | 0.302 |
| Switch-I | 0.858 |
| Switch-II / SII-P | 3.402 |
| MOV 5 A contact residues | 2.527 |

解讀：Switch-II 的 RMSD 明顯高於 Switch-I 與 global average，符合 AMG 510/Sotorasib 在 KRAS G12C 中打開或穩定 Switch-II pocket 的挑戰設定。這也是量子訊號傳播模型應特別捕捉的區域。

## AMG 510 / MOV 接觸殘基

`6OIM` 中 `MOV` ligand 的 heavy atom 數：41。
`6OIM` 中 GDP heavy atom 數：28。

- MOV centroid 到 GDP centroid 距離：16.718 A
- MOV centroid 到 active-site centroid 距離：10.488 A
- 4OBE/6OIM 對齊後 GDP centroid shift：0.265 A

MOV 周圍最接近的 residues：

| Residue | 6OIM | 4OBE | MOV distance (A) | GDP distance (A) | Region | Ref. SII-P residue |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 12 | CYS | GLY | 1.805 | 3.961 | P-loop / nucleotide active site | yes |
| 16 | LYS | LYS | 2.765 | 2.789 | P-loop / nucleotide active site |  |
| 59 | ALA | ALA | 3.155 | 6.268 | active-site neighborhood |  |
| 68 | ARG | ARG | 3.156 | 12.801 | Switch-II / SII-P | yes |
| 60 | GLY | GLY | 3.16 | 8.768 | Switch-II / SII-P |  |
| 63 | GLU | GLU | 3.223 | 16.124 | Switch-II / SII-P |  |
| 96 | TYR | TYR | 3.27 | 8.636 | distal/core/surface | yes |
| 72 | MET | MET | 3.277 | 13.544 | Switch-II / SII-P |  |
| 103 | VAL | VAL | 3.36 | 18.312 | distal/core/surface | yes |
| 9 | VAL | VAL | 3.447 | 7.024 | distal/core/surface |  |
| 34 | PRO | PRO | 3.482 | 4.975 | Switch-I |  |
| 10 | GLY | GLY | 3.497 | 5.491 | P-loop / nucleotide active site |  |
| 99 | GLN | GLN | 3.507 | 15.756 | distal/core/surface | yes |
| 61 | GLN | GLN | 3.516 | 9.995 | Switch-II / SII-P |  |
| 95 | HIS | HIS | 3.551 | 14.902 | distal/core/surface | yes |
| 62 | GLU | GLU | 3.628 | 13.239 | Switch-II / SII-P |  |
| 58 | THR | THR | 3.941 | 5.212 | active-site neighborhood | yes |
| 100 | ILE | ILE | 4.138 | 13.95 | distal/core/surface |  |
| 69 | ASP | ASP | 4.28 | 16.74 | Switch-II / SII-P |  |
| 11 | ALA | ALA | 4.282 | 3.878 | P-loop / nucleotide active site |  |
| 13 | GLY | GLY | 4.323 | 2.893 | P-loop / nucleotide active site |  |
| 92 | ASP | ASP | 4.708 | 10.532 | distal/core/surface |  |
| 64 | TYR | TYR | 5.14 | 17.892 | Switch-II / SII-P | yes |
| 35 | THR | THR | 5.339 | 6.901 | Switch-I |  |
| 37 | GLU | GLU | 5.622 | 8.686 | Switch-I |  |
| 78 | PHE | PHE | 5.745 | 13.275 | distal/core/surface |  |
| 97 | ARG | ARG | 5.904 | 14.794 | distal/core/surface |  |
| 8 | VAL | VAL | 6.169 | 6.814 | distal/core/surface |  |
| 7 | VAL | VAL | 6.25 | 11.066 | distal/core/surface |  |
| 14 | VAL | VAL | 6.318 | 3.423 | P-loop / nucleotide active site |  |

完整表格輸出：`analysis/kras_g12c/kras-g12c-6oim-amg510-mov-contact-residues.csv`

## 殘基接觸圖維度

| Structure | Nodes | Edges | Adjacency matrix | Avg degree | Max degree | Density | Components |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 4OBE chain A | 169 | 808 | 169 x 169 | 9.562 | 17 | 0.05692 | 1 |
| 6OIM chain A | 167 | 809 | 167 x 167 | 9.689 | 17 | 0.05837 | 1 |

圖資料輸出：

- `analysis/kras_g12c/kras-g12c-4obe-residue-contact-graph-8a.csv`
- `analysis/kras_g12c/kras-g12c-6oim-residue-contact-graph-8a.csv`

這個 adjacency matrix 維度可直接對應到挑戰要求的 connectivity matrix prototype。若後續改用量子 walk、Hamiltonian evolution 或 variational circuit，可把此 residue graph 作為拓撲輸入。

## 對量子挑戰的建議建模重點

1. **輸入應從 4OBE 出發，而不是使用 6OIM 的 MOV 坐標。**
   `6OIM` 的 MOV contact residues 只能作為 validation label，不能洩漏到 blind prediction feature。

2. **Residue indexing 要固定。**
   4OBE 與 6OIM chain A 有共同 residue numbering，但第 12 位是關鍵差異：4OBE 為 GLY，6OIM 為 CYS。報告與 hit list 應保留 PDB residue number、chain ID 與 residue name。

3. **Switch-II pocket 不只是局部口袋偵測問題。**
   MOV 5 A contacts 同時包含 P-loop、Switch-II 與 distal/core residues。好的 connectivity metric 應該能把 active-site/nucleotide 狀態與遠端 Switch-II pocket 聯繫起來。

4. **建議 baseline。**
   建議先以 4OBE chain A 建立 8 A residue contact graph，輸出 graph diffusion、shortest path、Laplacian heat kernel 或 random walk baseline，再與量子 metric 比較。

5. **建議 submission output。**
   對 KRAS G12C 的 top hit list 可先用 `6OIM` MOV 5 A/6 A contact residues 作為 ground-truth set，評估 predicted residues 是否富集於 Switch-II pocket 周邊。

## 產出檔案

- JSON summary: `analysis/kras_g12c/kras-g12c-4obe-6oim-dataset-summary.json`
- MOV contact CSV: `analysis/kras_g12c/kras-g12c-6oim-amg510-mov-contact-residues.csv`
- 4OBE contact graph CSV: `analysis/kras_g12c/kras-g12c-4obe-residue-contact-graph-8a.csv`
- 6OIM contact graph CSV: `analysis/kras_g12c/kras-g12c-6oim-residue-contact-graph-8a.csv`

