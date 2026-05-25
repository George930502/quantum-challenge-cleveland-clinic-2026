# Tian et al. 2023 - PASSer：快速蛋白質異位位點預測伺服器

## 基本資料

- 論文：PASSer: fast and accurate prediction of protein allosteric sites
- 作者：Hao Tian, Sian Xiao, Xi Jiang, Peng Tao
- 期刊：Nucleic Acids Research
- 年份：2023
- DOI：https://doi.org/10.1093/nar/gkad303
- 本地 PDF：`docs/literature/classical-baselines/papers/07_tian_2023_passer.pdf`
- 抽取文字：`docs/literature/classical-baselines/extracted/07_tian_2023_passer.txt`
- 引用數：約 67 次 OpenAlex，查核日期 2026-05-25
- 本任務排名：第 4 名

## 為什麼契合挑戰賽

PASSer 是最適合快速建立 ML/server baseline 的方法。它接受 PDB ID 或 user-uploaded PDB files，能在 seconds 級別輸出 top-3 predicted allosteric pockets。對 challenge 而言，PASSer 可以提供一個「現成 classical ML benchmark」：不需要先實作完整 graph physics，只要輸入 apo PDB 結構，就能得到口袋排名。

它和 challenge 的契合點：

- 使用 protein structure 與 detected pockets，符合 apo PDB input。
- 提供 top pockets 與 pocket residues，容易轉成 hit list。
- 包含 GCNN、XGBoost、AutoGluon、LambdaMART learning-to-rank 等 classical ML 模型。
- 有訓練資料準備 scripts 與 PASSerRank GitHub/Zenodo data availability，可追蹤 reproduce。
- Nucleic Acids Research web-server paper，工具可用性與社群可見度較高。

## 方法摘要

PASSer 伺服器整合三類已訓練模型：

1. **Ensemble model**：XGBoost 使用 19 個 pocket physical/chemical descriptors；GCNN 使用每個 pocket 的 atomic graph 學 local connectivity；最後平均兩者 probability。
2. **AutoML model**：用 AutoGluon 組合多個 base models，例如 SVM、random forest 等。
3. **Learning-to-rank model**：用 LambdaMART/LightGBM 對同一蛋白中的 pockets 依 allosteric relevance 排名。

輸入可以是 RCSB PDB ID 或自訂 PDB file。系統先用 fpocket-like pocket detection 找候選 pockets，再對每個 pocket 產生 probability 或 rank score。輸出包含 top three pockets、probability/score、pocket structure visualization，以及可下載的 protein/pocket PDB files 與結果表。

## 實驗與工具狀態

論文指出 PASSer 自 2020 launch 後已有超過 49,000 visits 與 6,200 jobs。PASSer 2023 NAR 版本整合了先前三個模型：

- PASSer 2021：XGBoost + GCNN ensemble。
- PASSer2.0 2022：AutoGluon AutoML。
- PASSerRank 2023：learning-to-rank。

資料來源包含 ASD、ASBench、CASBench 等 allosteric-site datasets。論文也說明資料清理與 pocket labeling workflow：以 modulator 和 pockets 的 center-of-mass distance 判定最接近 modulator 的 pocket 為 allosteric positive，其餘為 negative。

## 可轉成 baseline 的方式

建議把 PASSer 當成「現成 ML baseline」：

1. 將 apo PDB 結構輸入 PASSer 或 CLI。
2. 使用 ensemble learning 與 learning-to-rank 兩種模型，各自產生 top pockets。
3. 將 top pockets 的 residues 展開成 residue-level ranked list。
4. 對 KRAS/BCR-ABL1 validation contact residues 計算 top-1/top-3 pocket hit 與 top-k residue overlap。
5. 若可能，保留 PASSer 的 pocket probability 作為 score，與 quantum-inspired score 做 calibration 比較。

對 challenge 輸出格式：

- Connectivity Matrix：PASSer 不直接提供 connectivity matrix；可使用 pocket atomic graph 或 fpocket-derived pocket descriptors 作為 auxiliary baseline，不建議把它當 matrix baseline。
- Hit List：top three pockets 與其 residues。
- Report：標明使用哪一個 PASSer model，因為 ensemble、AutoML、LTR 的分數意義不同。

## 對三個資料集的預期表現

- KRAS G12C：中等。若 apo `4OBE` 未顯示 Switch-II cryptic pocket，PASSer 可能因 pocket detection 階段漏掉候選 pocket。
- BCR-ABL1：中高。Asciminib myristoyl pocket 是明確 binding pocket，PASSer 應有機會作為強 ML baseline。
- Cardiac Myosin：中等。大蛋白可輸入，但 allosteric mechanical site 未必是典型小分子 pocket；且目前 validation label 不可靠。

## 限制

- 主要是 pocket-level ML predictor，不是 signal-propagation model。
- 可能有 dataset bias：ASD/ASBench/CASBench 的 pocket definition 與 challenge 的 apo-to-holo blind prediction 不完全一致。
- 若候選 pocket detection 失敗，後續 ML 模型無法挽救。
- 不直接輸出 residue-residue connectivity matrix，因此不能單獨滿足 challenge 的 matrix 要求。
- 使用 webserver 時需記錄模型版本與輸出檔，避免不可重現。

## 對後續 quantum-inspired pipeline 的啟發

PASSer 最適合當 practical baseline，而不是 mechanistic baseline。它能回答一個實務問題：單純 ML pocket predictor 在 challenge labels 上能達到什麼水準？若 quantum-inspired pipeline 只比 PASSer 多了 connectivity matrix，但 hit recovery 不如 PASSer，就需要重新檢查 quantum metric 是否真的捕捉 allosteric relevance。

可用比較方式：

- PASSer top-3 pocket overlap vs quantum top-5 residue/hotspot overlap；
- PASSer probability vs quantum connectivity score；
- ML pocket descriptors vs quantum graph spectral descriptors；
- PASSer false positives 作為後續 quantum method 的負例分析。
