# Amor et al. 2016 - Bond-to-Bond Propensity：以能量加權原子圖預測異位位點與傳播作用

## 基本資料

- 論文：Prediction of allosteric sites and mediating interactions through bond-to-bond propensities
- 作者：B. R. C. Amor, M. T. Schaub, S. N. Yaliraki, M. Barahona
- 期刊：Nature Communications
- 年份：2016
- DOI：https://doi.org/10.1038/ncomms12477
- 本地 PDF：`docs/literature/classical-baselines/papers/02_amor_2016_bond_to_bond_propensities.pdf`
- 抽取文字：`docs/literature/classical-baselines/extracted/02_amor_2016_bond_to_bond_propensities.txt`
- 引用數：約 113 次 OpenAlex，查核日期 2026-05-25
- 本任務排名：第 2 名

## 為什麼契合挑戰賽

這篇是最強的 graph-theoretic physics baseline。它從 protein structure 建立 atomistic energy-weighted graph，將 covalent bonds 與 non-covalent weak interactions 都視為帶權邊，並用 edge-to-edge transfer matrix 衡量 active site perturbation 對任意 bond 的非局部影響。

它和 challenge 的契合點：

- 不需要 MD trajectory；主要輸入是 PDB 結構與 active site 定義。
- 輸出可包含 bond score、residue score、site/pocket score、communication pathway。
- 直接處理 long-range coupling，符合「allosteric signal propagation」問題。
- 可把 residue score 對應到 top-k hit list，也可把 edge-to-edge transfer matrix 或 residue-aggregated propensity 當作 classical connectivity matrix。

## 方法摘要

論文方法可拆成五步：

1. 從 PDB 建立 atomistic graph。
2. 節點是 atoms；邊包含 covalent bonds、hydrogen bonds、salt bridges、hydrophobic tethers、electrostatic interactions。
3. 邊權重由 interatomic potentials 或 force-field-like interaction energies 估計。
4. 以 graph Laplacian 與 edge-space Green's function 建立 edge-to-edge transfer matrix。
5. 從 active-site ligand/protein interactions 出發，計算每個 bond 的 propensity，再聚合成 residue score 或 allosteric site score。

其核心概念是：若某些遠端 bonds/residues 對 active-site perturbation 有高 propensity，代表它們在 protein graph 上與 active site 強耦合，可能位於 allosteric site 或傳播路徑。

## 實驗與驗證

論文先分析三個代表性蛋白：caspase-1、CheY、h-Ras，並進一步用 20 個 known allosteric proteins 測試。

重點結果：

- Caspase-1：原子級能量圖能找到 allosteric inhibitor pocket，6A residue-residue interaction network 反而找不到。這顯示單純 C-alpha cutoff graph 對某些蛋白不足。
- CheY：propensity 能標示與 phosphorylation signaling 相關的 bonds/residues。
- h-Ras：結構水分子可能是 active/allosteric sites 之間傳播路徑的一部分；這對 KRAS G12C 有直接警示價值。
- 20-protein test set：19/20 至少被一個統計量辨識出 allosteric site；15/20 被四個統計量中的至少三個支持。
- 計算可近似線性擴展，論文指出約 100,000 atoms 的 complex 可在 desktop minutes 級別完成。

## 可轉成 baseline 的方式

建議把這篇實作為「高解析 classical baseline」，和 Ohm 的 residue-contact baseline 互補：

1. **Atomistic graph baseline**：從 PDB 建 atoms/bonds graph，保留 covalent backbone、hydrogen bonds、salt bridges、hydrophobic/electrostatic weak interactions。
2. **Residue-aggregated score**：把 bond propensity 加總或平均到 residue，形成 residue-level ranking。
3. **Pocket/site score**：將 validation ligand contact residues 或 fpocket pocket residues 的 score 聚合成 site score。
4. **Graph ablation**：比較 atomistic graph、C-alpha graph、8A residue contact graph，測試本 challenge 現有 graph 是否足以重現 signal。

對 challenge 輸出格式：

- Connectivity Matrix：可用 edge-to-edge transfer matrix，或將 atom/bond score 聚合成 residue-residue influence matrix。
- Hit List：用 residue propensity quantile score 排名，或用 top-propensity residues 聚類。
- Report：特別說明 active site seed、graph edge types、是否納入 structural water。

## 對三個資料集的預期表現

- KRAS G12C：高契合。論文含 h-Ras 案例，並指出 structural water 可影響 allosteric pathway。KRAS Switch-II pocket 屬於這類需要化學細節的難題。
- BCR-ABL1：高契合但實作成本較 Ohm 高。Asciminib myristoyl pocket 與 kinase active site 長距耦合，適合 edge-propensity analysis。
- Cardiac Myosin：理論上可處理大型 complex，但 atomistic graph 對 5TBY/6C1H 會較重；建議先 domain decomposition 或 coarse-grained variant。

## 限制

- 需要 active site 定義；若 seed 定義錯誤，propensity ranking 會偏移。
- 實作比 residue contact graph 顯著複雜，需要穩定的 bond/interaction detection 與 edge weighting。
- 是否納入 water、cofactor、ligand-like components 必須和 challenge blind-input 規則一致。validation ligand 不可進入 input graph。
- 對現有 `analysis/*-residue-contact-graph-8a.csv` 不能直接套用完整原子級方法，需回到 PDB/mmCIF 建圖。

## 對後續 quantum-inspired pipeline 的啟發

這篇提供一個明確的「edge-space propagation」對照。後續量子啟發方法不一定只在 residue nodes 上傳播，也可把 protein graph 的 bonds/interactions 當作 Hilbert-space basis 或 line graph basis：

- bond-to-bond transfer matrix vs quantum walk on line graph；
- propensity quantile vs quantum hitting amplitude/significance；
- atomistic energy-weighted Laplacian vs Hamiltonian construction；
- site-level quantile score vs quantum metric enrichment。

它適合作為高解析但較重的 benchmark，用來檢驗量子啟發方法是否真的超越精緻 classical graph model。
