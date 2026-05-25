# Wang et al. 2020 - Ohm：單一蛋白質內異位通訊映射

## 基本資料

- 論文：Mapping allosteric communications within individual proteins
- 作者：Jian Wang, Abha Jain, Leanna R. McDonald, Craig Gambogi, Andrew L. Lee, Nikolay V. Dokholyan
- 期刊：Nature Communications
- 年份：2020
- DOI：https://doi.org/10.1038/s41467-020-17618-2
- 本地 PDF：`docs/literature/classical-baselines/papers/01_wang_2020_ohm_mapping_allosteric_communications.pdf`
- 抽取文字：`docs/literature/classical-baselines/extracted/01_wang_2020_ohm_mapping_allosteric_communications.txt`
- 引用數：約 203 次 OpenAlex；Nature 頁面顯示約 209 次，查核日期 2026-05-25
- 本任務排名：第 1 名

## 為什麼高度契合挑戰賽

Ohm 是五篇中最貼近 Cleveland Clinic challenge 的 classical baseline。原因有三點：

1. 輸入只需要蛋白質 3D 結構，不依賴 MD trajectory，符合 challenge 禁止使用古典 MD 軌跡作為輸入的限制。
2. 方法核心直接建立 residue-residue contact matrix 與 perturbation propagation probability matrix，最後輸出 residue-level allosteric coupling intensity, ACI。這和 challenge 要求的 `N x N` connectivity matrix 與 residue-level hit list 很容易對接。
3. 論文不只做 pocket prediction，也輸出 allosteric pathways、critical coupled residues、pairwise allosteric correlations；這些輸出可直接轉成 3D residue map 與解釋性報告。

對目前資料集而言，Ohm 可直接以 apo 結構建立接觸矩陣：KRAS `4OBE` chain A 169 nodes、BCR-ABL1 `1OPL` chain A 451 nodes、Cardiac Myosin `5TBY` chain A 954 nodes。模型輸出可和 KRAS `MOV`、BCR-ABL1 `AY7` 的 8A validation contact residues 做 top-k recovery、AUROC、AUPRC 或 enrichment test。

## 方法摘要

Ohm 的流程是：

1. 從 PDB 3D 結構抽取 residue-residue contacts。
2. 計算 residue pair 之間的 contact strength，並以 residue atom 數做正規化。
3. 將 contact matrix 轉成 perturbation propagation probability matrix `Pij`。
4. 從 active site 或指定 perturbation site 出發，重複隨機傳播擾動。
5. 統計每個 residue 被擾動影響的頻率，定義為 ACI。
6. 用 ACI 與 3D 座標聚類，產生 allosteric hotspot。
7. 若已知 active site 與 allosteric site，紀錄傳播路徑並找出 critical residues。

論文也提供 pairwise residue correlation 模式：當 active site 或 allosteric site 都未知時，可計算 residue pair 的 allosteric correlation，再用 clustering 分析蛋白質內部的耦合區域。這對 c-Myc/Max 這類缺乏明確 validation ligand 的探索型標的特別有用。

## 實驗與驗證

論文以 20 個已知 allosterically regulated proteins 做 backward validation，涵蓋 monomer、dimer、trimer、tetramer、hexamer、dodecamer 等不同 oligomeric states。它也用 CheY 的 NMR CHESCA experimental correlation 做 forward validation，並用 mutagenesis 破壞 allosteric communication 來檢查 Ohm prediction 是否有實驗對應。

重點結果：

- Ohm 以 structure-only network 分析出 allosteric sites、pathways、critical residues 與 residue-residue correlations。
- Caspase-1 與 CheY 案例顯示 ACI hotspot 能落在已知 functional/allosteric regions。
- CheY 的 residue-residue allosteric correlation 與 NMR CHESCA 有可比對關係。
- 論文提供 Ohm webserver 與 source code 位置，利於 baseline reproduce。

## 可轉成 baseline 的方式

建議在本 challenge 中實作三個 Ohm baseline 版本：

1. **Known-active-site baseline**：若可從 apo structure 或文獻定義 active site，從 active site 出發計算 ACI，排名所有 residues。KRAS 可從 nucleotide/GTPase switch region 定義 perturbation seed；BCR-ABL1 可從 kinase ATP/catalytic site 定義 seed。
2. **Blind pairwise baseline**：不指定 seed，計算 residue-residue allosteric correlation matrix，再用 graph clustering 或 centrality 找 hotspot。這更接近 c-Myc 探索任務。
3. **Pocket aggregation baseline**：先算 residue ACI，再將 residue score 聚合到 fpocket 或 geometric pocket，以 pocket score 排名。

對 challenge 輸出格式：

- Connectivity Matrix：使用 Ohm 的 perturbation propagation probability matrix 或 pairwise allosteric correlation matrix。
- Hit List：使用 ACI top residues，或 ACI clustering 後的 top hotspot residues。
- Methodological Report：說明 contact-count normalization、propagation repeat count、seed selection、是否排除 sequence-adjacent contacts。

## 對三個資料集的預期表現

- KRAS G12C：高契合。Sotorasib Switch-II pocket 是典型 distal/cryptic communication problem。Ohm 可測試 active site/GDP region 到 Switch-II pocket contacts 的 ACI enrichment。
- BCR-ABL1：高契合。myristoyl pocket 是遠端 allosteric pocket，適合 active/catalytic site 到 distal pocket 的 propagation baseline；需明確排除 `NIL` ATP-site inhibitor label。
- Cardiac Myosin：中等契合但 label 風險高。Ohm 可處理大型 contact graph，但目前 `6C1H` 未確認 Mavacamten-like ligand label，應以 exploratory communication map 為主。

## 限制

- 若使用 known active site seed，baseline 已經引入一定生物先驗；評估時需清楚標記。
- Stochastic propagation 需要固定 random seed 與重複次數，否則 top-ranked residues 可能有微小波動。
- Contact definition 與 normalization 會影響結果，需和 quantum-inspired pipeline 共用同一份 graph preprocessing。
- Webserver/code longevity 需要確認；若不可用，演算法仍可由論文公式重建。

## 對後續 quantum-inspired pipeline 的啟發

Ohm 是最適合被量子啟發化的 classical baseline。它本質上已經把蛋白質抽象成 contact probability network，並模擬 perturbation propagation。後續可把其 transition matrix 對應到：

- classical random walk vs quantum walk；
- Markov propagation vs unitary/CTQW propagation；
- ACI frequency vs quantum hitting probability；
- allosteric correlation matrix vs quantum correlation/fidelity matrix。

因此建議把 Ohm 作為第一個實作 baseline，也是後續 quantum-inspired pipeline 的主要比較對象。
