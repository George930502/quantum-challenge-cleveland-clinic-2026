# Kumar/Kaynak et al. 2023 - APOP：蛋白質生物組裝體的異位口袋預測

## 基本資料

- 論文：Predicting allosteric pockets in protein biological assemblages
- 作者：Ambuj Kumar, Burak T. Kaynak, Karin S. Dorman, Pemra Doruker, Robert L. Jernigan
- 期刊：Bioinformatics
- 年份：2023
- DOI：https://doi.org/10.1093/bioinformatics/btad275
- 本地 PDF：`docs/literature/classical-baselines/papers/06_kaynak_2023_apop.pdf`
- 抽取文字：`docs/literature/classical-baselines/extracted/06_kaynak_2023_apop.txt`
- 引用數：約 27 次 OpenAlex，查核日期 2026-05-25
- 本任務排名：第 3 名

## 為什麼契合挑戰賽

APOP 是五篇中最適合作為「現代 pocket-level classical baseline」的方法。它不只看口袋幾何，也用 Gaussian Network Model, GNM 模擬 ligand binding 對全域模式的擾動，並加入 pocket hydrophobic density 作為 druggability/allosteric likelihood 特徵。

它和 challenge 的契合點：

- 可直接從 PDB 結構輸入，不需要 MD trajectory。
- 使用 C-alpha elastic network，和 challenge 的 elastic network hypothesis 相容。
- 支援 biological assemblies，對 Cardiac Myosin 或 BCR-ABL1 domain/assembly 問題比單鏈 pocket model 更實用。
- 輸出是 ranked pockets，可直接形成 top-5 allosteric hit list。
- 開源 Python package 與 webserver 可用，利於 reproducibility。

## 方法摘要

APOP 流程：

1. 用 Fpocket 在 protein structure 中找 candidate pockets。
2. 建立 GNM elastic network，C-alpha atoms 是 nodes，10A cutoff 建 contact matrix。
3. 對每個 pocket 模擬 ligand binding：將 pocket-lining residues 之間的 springs stiffen。
4. 比較 perturbation 前後前五個 global modes 的 eigenvalue shifts。
5. 同時使用 pocket local hydrophobic density。
6. 將 global mode shift z-score 與 hydrophobicity z-score 合併，得到 pocket allosteric propensity score。

這個設計很適合 challenge：它把 allosteric site 定義成「能顯著改變 global dynamics 的 pocket」，而不是單純「幾何上像 pocket」。

## 實驗與驗證

APOP 在 104 個 test cases 上評估，包含 monomers 與 multimeric assemblages。論文報告 92/104 個案例能在 top-3 pocket 中找到 known allosteric pocket，成功率 88.5%。在 50 個 bound allosteric ligand dataset 中，APOP top-3 success rate 為 84% (42/50)，高於 AlloPred 的 68% (34/50) 與 PASSer 的 76% (38/50)。

值得注意的是，APOP 對 ABL kinase 有直接相關案例：論文 Figure 3 展示 ABL kinase 的 allosteric ligand-binding pocket 可被 APOP 排在 rank 1、rank 2 或 rank 3。這與本 challenge 的 BCR-ABL1 Asciminib myristoyl pocket 任務高度相關。

## 可轉成 baseline 的方式

建議將 APOP 作為 pocket-level baseline：

1. 對 apo input structure 跑 Fpocket 取得 pockets。
2. 用 APOP 對所有 pockets 排名。
3. 將 top-ranked pockets 的 residue list 轉成 residue-level hit list。
4. 和 validation ligand contacts 做 overlap：例如 KRAS `MOV` 49 residues、BCR-ABL1 `AY7` 46 residues。
5. 若 pocket output 是 pocket-level，評估可用 top-1/top-3 pocket hit、Jaccard overlap、best-pocket contact enrichment。

對 challenge 輸出格式：

- Connectivity Matrix：APOP 本身不直接輸出 residue-residue communication matrix；可用 GNM contact matrix 或 mode-shift-derived pocket perturbation matrix 作為 classical comparator。
- Hit List：top pockets 的 lining residues。
- Report：說明 pocket detection、GNM cutoff、global mode count、hydrophobic density aggregation。

## 對三個資料集的預期表現

- KRAS G12C：中高契合。Switch-II pocket 是 cryptic pocket；若 apo `4OBE` 的 pocket geometry 不明顯，Fpocket 可能漏檢，這會限制 APOP。
- BCR-ABL1：高契合。APOP 論文已有 ABL kinase allosteric pocket 案例，且 myristoyl pocket 是明確 pocket-level target。
- Cardiac Myosin：中高契合但 label 需確認。APOP 支援 assemblies，對大型蛋白與 biological assembly 有優勢；但目前 Mavacamten-like validation label 不明確。

## 限制

- APOP 依賴 Fpocket；若 allosteric site 是 cryptic pocket 且 apo 結構未形成可偵測 cavity，APOP 會失敗。
- 它輸出 pocket-level ranking，不是原生 residue-residue propagation matrix；若 challenge 評分重 residue-level matrix，需額外轉換。
- Hydrophobicity feature 對小分子 druggable pockets 有利，但對 mechanical regulatory sites 或 protein-protein interface allostery 可能偏弱。
- 引用數低於 Ohm、Allosite、AlloPred，因為較新；但方法與 challenge fit 高。

## 對後續 quantum-inspired pipeline 的啟發

APOP 可提供「pocket perturbation」框架：把每個 candidate pocket 視為一個 perturbation operator，觀察全域模式或 Hamiltonian spectrum 的變化。後續 quantum-inspired pipeline 可對比：

- GNM eigenvalue shift vs quantum Hamiltonian spectral shift；
- pocket stiffening vs local potential perturbation；
- hydrophobicity-adjusted score vs quantum score + physicochemical prior；
- top-pocket hit rate vs residue-level quantum connectivity enrichment。

因此 APOP 適合當作 pocket-ranking baseline，特別是 BCR-ABL1 與可能的大型 myosin assembly。
