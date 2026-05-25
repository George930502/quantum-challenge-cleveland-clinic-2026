# Classical Baseline Literature Summary

## 任務範圍

本次 literature research 只聚焦 classical baseline，不納入 quantum-inspired pipeline 文獻。篩選目標是找出最適合 Cleveland Clinic Global Quantum + AI Challenge 2026 的五篇論文，用於後續先建立 classical baseline，再發展 quantum-inspired pipeline。

Challenge 的核心要求是：從 apo PDB 結構出發，建立 residue/contact/coarse-grained network，預測 allosteric signal propagation、遠端 allosteric site 或 residue hit list。最重要評估標準是已知 validation allosteric ligand contact residues 是否在 top-ranked hits 中出現。

本地 challenge 與資料集依據：

- `docs/challenge/cleveland-clinic-quantum-ai-challenge-2026-details.zh-TW.md`
- `docs/research/allosteric-challenge-three-dataset-feature-analysis.zh-TW.md`
- `analysis/kras_g12c/kras_g12c-4obe-6oim-dataset-analysis.zh-TW.md`
- `analysis/bcr_abl1/bcr_abl1-1opl-5mo4-dataset-analysis.zh-TW.md`
- `analysis/cardiac_myosin/cardiac_myosin-5tby-6c1h-dataset-analysis.zh-TW.md`

## 本地資料集重點

| Dataset | Blind input | Validation | 任務 | Input graph | Validation labels |
| --- | --- | --- | --- | ---: | --- |
| KRAS G12C | `4OBE` chain A | `6OIM` chain A | 找出 Sotorasib/AMG 510 Switch-II pocket | 169 nodes / 808 edges | `MOV` 8A contacts, 49 residues |
| BCR-ABL1 | `1OPL` chain A | `5MO4` chain A | 找出 Asciminib myristoyl pocket | 451 nodes / 2166 edges | `AY7` 8A contacts, 46 residues |
| Cardiac Myosin | `5TBY` chain A | `6C1H` chain P | 找出 Mavacamten-like mechanical regulatory site | 954 nodes / 4126 edges | 高風險；未偵測到 Mavacamten-like ligand |

KRAS 與 BCR-ABL1 應作為主要 benchmark。Cardiac Myosin 目前適合做 exploratory analysis，除非 organizer 確認 validation label。

## 搜尋與篩選準則

本次排序依照下列權重：

1. **挑戰賽目標契合程度**：最高權重。優先選擇可從 static/apo structure、contact network、elastic network 或 residue/pocket graph 預測 allosteric site 的方法。
2. **輸出可評分性**：能否產生 residue ranking、pocket ranking、connectivity matrix、communication path 或 allosteric hotspot。
3. **不依賴 MD trajectory**：避免違反 challenge 限制。
4. **論文等級與工具可用性**：Nature Communications、Bioinformatics、Nucleic Acids Research、BMC Bioinformatics 等。
5. **引用數**：作為成熟度指標，但低於 challenge fit。

引用數主要採 OpenAlex `cited_by_count`，查核日期 2026-05-25；個別頁面顯示數字可能略有差異。

## 最終五篇排序

| Rank | Paper | Year | Venue | Citations | Fit | 核心理由 |
| ---: | --- | ---: | --- | ---: | ---: | --- |
| 1 | Wang et al., Ohm | 2020 | Nature Communications | 約 203 | 5/5 | structure-only residue contact propagation，直接輸出 ACI、pathway、correlation |
| 2 | Amor et al., bond-to-bond propensity | 2016 | Nature Communications | 約 113 | 5/5 | atomistic energy-weighted graph，預測 allosteric sites 與 mediating interactions |
| 3 | Kumar/Kaynak et al., APOP | 2023 | Bioinformatics | 約 27 | 4.5/5 | GNM pocket perturbation + hydrophobicity，支援 biological assemblies |
| 4 | Tian et al., PASSer | 2023 | Nucleic Acids Research | 約 67 | 4/5 | 快速 ML/server baseline，top pocket prediction，工具可用 |
| 5 | Greener and Sternberg, AlloPred | 2015 | BMC Bioinformatics | 約 133 | 4/5 | NMA perturbation + Fpocket/SVM，經典 active-site-aware pocket baseline |

## 下載的 PDF

- `docs/literature/classical-baselines/papers/01_wang_2020_ohm_mapping_allosteric_communications.pdf`
- `docs/literature/classical-baselines/papers/02_amor_2016_bond_to_bond_propensities.pdf`
- `docs/literature/classical-baselines/papers/06_kaynak_2023_apop.pdf`
- `docs/literature/classical-baselines/papers/07_tian_2023_passer.pdf`
- `docs/literature/classical-baselines/papers/05_greener_2015_allopred.pdf`

另有兩篇候選文獻曾被評估，但未納入最終 top 5；其 OUP PDF 直接請求回傳 403，因此未保留本地 PDF：

- Goncearenco et al. 2013, SPACER。
- Huang et al. 2013, Allosite。

## 五篇方法的 baseline 定位

### 1. Ohm：主要 residue-level propagation baseline

Ohm 應作為第一個實作 baseline。它最接近 challenge 的 desired output：從 contact matrix 產生 propagation probability、ACI residue score、allosteric hotspots、critical residues、pairwise correlations。

建議輸出：

- residue-residue propagation probability matrix；
- active-site-seeded ACI residue ranking；
- blind pairwise allosteric correlation clustering；
- top-5 residue/hotspot hit list。

### 2. Bond-to-bond propensity：高解析 atomistic graph baseline

這篇應作為高解析 physics baseline。它比 C-alpha graph 更重，但能測試化學細節是否對 KRAS/BCR-ABL1 的 allosteric path recovery 有幫助。

建議輸出：

- atomistic graph edge-to-edge transfer matrix；
- bond propensity；
- residue-aggregated propensity；
- site/pocket-level quantile score。

### 3. APOP：現代 pocket-level ENM baseline

APOP 應作為 pocket-ranking baseline，尤其適合 BCR-ABL1 與大型 biological assemblies。它不直接提供 connectivity matrix，但能提供 top-ranked pockets，和 validation ligand contacts 直接比對。

建議輸出：

- Fpocket candidate pockets；
- GNM mode-shift pocket scores；
- hydrophobicity-adjusted allosteric propensity；
- top-3/top-5 pocket residues。

### 4. PASSer：快速 ML/server baseline

PASSer 應作為 practical ML baseline。它可快速檢查現成 ML allosteric site predictor 在 challenge labels 上的表現。

建議輸出：

- ensemble learning top pockets；
- learning-to-rank top pockets；
- pocket probabilities/rank scores；
- pocket residue hit overlap。

### 5. AlloPred：active-site-aware NMA perturbation baseline

AlloPred 適合作為 classic ENM/NMA baseline。它需要 active site residues，因此應明確標註 seed source，避免和 validation allosteric label 混淆。

建議輸出：

- Fpocket pockets；
- active-site response under pocket perturbation；
- SVM pocket ranking；
- top pocket residue list。

## 對 challenge 的實作建議

第一階段 classical baseline 實作順序：

1. **Ohm-like residue contact propagation**  
   使用現有 `analysis/*-residue-contact-graph-8a.csv` 直接建 graph，最快可完成 residue ranking 與 connectivity matrix。

2. **APOP-like pocket perturbation baseline**  
   新增 fpocket 或替代 pocket detection，對 KRAS/BCR-ABL1 產生 pocket-level hit list。

3. **PASSer external/tool baseline**  
   若 webserver 或 CLI 可用，跑 apo PDB 並保存結果；若不可用，只保留為文獻 baseline，不阻塞本地 pipeline。

4. **AlloPred-style NMA baseline**  
   用 active-site-aware perturbation 產生 pocket ranking，適合和 quantum perturbation response 比較。

5. **Bond-to-bond atomistic baseline**  
   作為高解析版本，在 KRAS 與 BCR-ABL1 上優先測試；Cardiac Myosin 需先做 domain decomposition。

## 評估設計

對 KRAS 與 BCR-ABL1 建議使用：

- top-5 / top-10 residue hit overlap；
- validation contact residue enrichment；
- AUROC / AUPRC；
- mean reciprocal rank of first validation residue；
- pocket-level hit：top-1/top-3 pocket 是否覆蓋 validation ligand contacts；
- 3D visualization：將 scores 映射到 apo structure。

對 Cardiac Myosin：

- 先不做嚴格 allosteric ligand contact scoring；
- 使用 exploratory hotspot map、domain-level communication analysis；
- 等 organizer 確認 Mavacamten-like validation structure/label 後再納入主 benchmark。

## 主要 insight 統整

1. **最公平的 classical baseline 不應只做 geometric pocket detection**  
   Challenge 的核心是 allosteric signal propagation，因此 Ohm 與 bond-to-bond propensity 比 Allosite/PASSer 類純 pocket predictor 更關鍵。

2. **pocket-level 與 residue-level baseline 要分開評估**  
   Ohm/bond-to-bond 可產生 residue score；APOP/PASSer/AlloPred 主要產生 pocket score。評估時應同時報告 residue-level 與 pocket-level metrics，避免混淆。

3. **active site seed 是重要變因**  
   Ohm、bond-to-bond、AlloPred 可能需要 active site 定義。這不是 validation leakage，但必須在 report 中明確記錄 seed residue source。

4. **cryptic pocket 是 KRAS 的主要難點**  
   APOP/PASSer/AlloPred 都依賴 candidate pocket detection；如果 apo `4OBE` 沒有清楚 Switch-II pocket，pocket predictor 可能漏掉。Ohm 與 bond-to-bond 比較不受候選 pocket detection 限制。

5. **BCR-ABL1 是最適合 pocket baseline 的資料集**  
   Asciminib myristoyl pocket 是明確 distal allosteric pocket，APOP、PASSer、AlloPred 很適合先跑。

6. **後續 quantum-inspired pipeline 的合理目標不是取代所有 classical model，而是超越最貼近的 graph propagation baseline**  
   最重要 comparator 應是 Ohm-like propagation 與 bond-to-bond graph propensity。若量子方法只比簡單 pocket ML 好，但比 Ohm 差，說服力不足。

## 後續建議

下一步建議直接進入 classical baseline 實作：

1. 以 Ohm-like propagation 為 MVP，使用現有 residue contact graph。
2. 建立 unified evaluation script，對 KRAS/BCR-ABL1 validation contacts 報告 top-k 與 enrichment。
3. 加入 APOP/PASSer/AlloPred 的 pocket-level baseline。
4. 最後再開始 quantum-inspired walk/spectral pipeline，並共用同一套 graph preprocessing 與 evaluation labels。
