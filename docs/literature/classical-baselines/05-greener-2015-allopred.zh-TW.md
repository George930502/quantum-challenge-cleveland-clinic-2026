# Greener and Sternberg 2015 - AlloPred：normal mode perturbation + pocket descriptors 的異位口袋預測

## 基本資料

- 論文：AlloPred: prediction of allosteric pockets on proteins using normal mode perturbation analysis
- 作者：Joe G. Greener, Michael J. E. Sternberg
- 期刊：BMC Bioinformatics
- 年份：2015
- DOI：https://doi.org/10.1186/s12859-015-0771-1
- 本地 PDF：`docs/literature/classical-baselines/papers/05_greener_2015_allopred.pdf`
- 抽取文字：`docs/literature/classical-baselines/extracted/05_greener_2015_allopred.txt`
- 引用數：約 133 次 OpenAlex，查核日期 2026-05-25
- 本任務排名：第 5 名

## 為什麼契合挑戰賽

AlloPred 是經典的 ENM/NMA + pocket ML baseline。它的定位介於 APOP 與 PASSer 之間：比單純 pocket descriptor 更有 dynamics/perturbation 意義，但比 Ohm/bond-to-bond 更偏 pocket classification。

它和 challenge 的契合點：

- 使用 protein structure、Fpocket pockets、normal mode perturbation，不需要 MD trajectory。
- 能輸出 pocket ranking，可轉成 top-k hit list。
- 需要 active site residues，這對 KRAS/BCR-ABL1 可從生物學先驗定義。
- 已有 40-protein test set 結果，可作為歷史 baseline。

## 方法摘要

AlloPred 流程：

1. 使用 Fpocket 找出 protein surface pockets。
2. 使用 normal mode analysis 建立 protein equilibrium fluctuation model。
3. 對每個候選 pocket 施加 perturbation：提高 pocket residues 相關 pair 的 spring constant，模擬 modulator binding 限制局部彈性。
4. 量測該 perturbation 對 active site residues normal modes/flexibility 的影響。
5. 將 NMA perturbation features 與 Fpocket descriptors 合併，放入 SVM model。
6. 對 pockets 排名，輸出最可能 allosteric pockets。

使用的 features 包含 alpha sphere 數、SASA、hydrophobic density、Fpocket rank、distance to active site、pocket residue count、normal-mode perturbation measures 等。

## 實驗與驗證

論文以 known allosteric proteins 建立資料集，並在 40-protein test set 上測試：

- AlloPred 在 23/40 proteins 中將 allosteric pocket 排名第 1。
- 28/40 proteins 中 allosteric pocket 排名第 1 或第 2。
- AlloSite 在相同 comparison 中 top-1 命中 21/40。
- PARS top-1 命中 10/40，但因為 PARS 是 point/site prediction，不是 pocket prediction，直接比較需保守。
- 400-residue protein、約 15 pockets 的分析可在 5 分鐘內完成。

## 可轉成 baseline 的方式

建議將 AlloPred 作為「active-site-aware ENM pocket baseline」：

1. 對 apo structure 跑 Fpocket。
2. 定義 active site residues，不可使用 validation allosteric ligand contacts。
3. 對每個 pocket 做 normal mode perturbation。
4. 產生 pocket ranking。
5. 將 pocket residues 展開成 ranked residue list，和 validation contact residues 比較。

對 challenge 輸出格式：

- Connectivity Matrix：AlloPred 不直接產生 matrix；可輸出 ENM contact matrix、normal mode covariance matrix 或 perturbation response matrix 作為輔助。
- Hit List：top-ranked pockets 及 pocket residues。
- Report：需列出 active site seed、Fpocket parameters、normal modes 數量、SVM model/source 是否可重現。

## 對三個資料集的預期表現

- KRAS G12C：中等到中高。若 Switch-II pocket 被 Fpocket 找到，active-site-aware perturbation 可幫助排序；若 apo pocket cryptic，仍可能漏掉。
- BCR-ABL1：高。AlloPred 對 active-site-to-distal-pocket 的架構適合 kinase allostery，且 active site residue 可由 kinase domain 文獻定義。
- Cardiac Myosin：中等。大型蛋白可能計算較慢，且 active site/mechanical site 定義不如 kinase/GTPase 清楚。

## 限制

- 需要 active site residues；對 c-Myc 或不明確 active site 的 target 不方便。
- 依賴 Fpocket，對 cryptic pocket 問題有同樣弱點。
- 使用 SVM 與舊資料集，可能不如近年的 PASSer/APOP。
- 它的輸出是 pocket-level，不是 residue-level communication path；解釋力不如 Ohm 或 bond-to-bond propensity。

## 對後續 quantum-inspired pipeline 的啟發

AlloPred 提供一個簡潔的 perturbation-response baseline：在候選 pocket 加 local stiffness，看 active site dynamics 是否改變。後續 quantum-inspired pipeline 可建立類似架構：

- pocket perturbation 改變 Hamiltonian；
- 比較 perturbation 前後 quantum spectrum、transition probability、state fidelity；
- 用 active-site response 作為 allosteric score；
- 再和 AlloPred 的 NMA perturbation score 比較。

因此 AlloPred 適合作為「以 active site 為錨點的 classical dynamics baseline」。
