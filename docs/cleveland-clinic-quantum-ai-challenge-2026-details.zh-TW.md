# Cleveland Clinic Global Quantum + AI Challenge 2026 競賽說明

原始文件：[`cleveland-clinic-quantum-ai-challenge-2026-statement.pdf`](./cleveland-clinic-quantum-ai-challenge-2026-statement.pdf)

## 競賽主題

本競賽題目為 **Unlocking undruggable targets: quantum simulation of allosteric signal propagation**，核心挑戰是運用量子演算法、量子啟發式方法或量子-古典混合方法，從蛋白質結構中預測異位調控訊號傳播路徑與潛在異位結合位點。

競賽由 Cleveland Clinic 提出，背景問題來自藥物研發早期的標的辨識與驗證階段。許多與疾病相關的蛋白質缺乏明顯、深層且適合小分子結合的活性位點，因此常被視為「不可成藥」標的。若能找出蛋白質表面遠離活性位點、但可透過異位訊號調控功能的隱藏口袋，將有機會讓過去難以開發的疾病標的重新進入藥物設計流程。

## 要解決的問題

傳統小分子藥物設計通常依賴靜態結構中的明顯結合口袋；然而許多蛋白質的活性位點可能過於平坦、暴露於溶劑中，或位於蛋白質-蛋白質交互作用介面，導致傳統 docking 或口袋偵測方法效果有限。

異位調控提供另一種策略：藥物不一定直接結合活性位點，而是結合遠端調控口袋，並透過蛋白質內部的動態連通性改變活性位點功能。問題在於，這類遠端訊號傳播通常需要長時間分子動力學模擬才能觀察，而完整 MD 模擬成本高、耗時長，且競賽明確要求不得依賴古典 MD 軌跡作為輸入。

本競賽希望參賽者建立一個「量子啟用的異位掃描器」：從靜態 PDB 結構出發，抽象成殘基或接觸網路，利用量子資訊傳播、非局域相關、干涉或其他可解釋的量子指標，推估哪些殘基或區域與活性位點具有高度動態連通性。

## 主要目標

最重要目標是 **最大化量子演算法辨識實驗驗證異位位點的預測準確率**。

參賽者需要設計可模擬蛋白質結構中訊號傳播的量子電路或等價方法，並輸出殘基排名。成功的解法應能讓已知遠端調控殘基取得統計上顯著高於隨機背景殘基與非功能性表面口袋的分數。

參賽者可自行定義量子指標，例如與量子態傳播、轉移機率、相關性、干涉、譜特徵或其他量子資訊量相關的 metric，但必須清楚說明該指標為何能作為生物訊號傳播的 proxy。

## 次要目標

除準確率外，競賽也重視實務可部署性：

- **抗雜訊能力**：方法需考量近期量子硬體的 gate error、有限 coherence time 與量測雜訊，並展示訊號傳播指標在雜訊下的穩定性。
- **可擴展性**：許多蛋白質若以殘基或原子一對一映射到 qubit，會超過現有硬體容量。解法需說明如何 coarse-grain 蛋白質結構，並證明壓縮後仍保留關鍵拓撲訊號。
- **可解釋性**：輸出需能被藥物化學家與結構生物學家理解與使用，尤其是 3D 視覺化的量子連通性圖與清楚的生物學解釋。
- **古典對照比較**：若適用，應與古典擴散模型、網路分析或其他 baseline 進行比較。

## 輸入資料

參賽者會取得來自 RCSB Protein Data Bank 的 benchmark 蛋白質結構。競賽要求使用 **未結合配體的 apo 結構** 作為輸入，盲測預測已知存在於 **藥物結合 holo 結構** 中的異位口袋位置。

最低必要目標如下：

| 標的 | 疾病領域 | 蛋白質類別 | 任務目標 | 輸入結構 | 驗證結構 |
| --- | --- | --- | --- | --- | --- |
| KRAS G12C | 腫瘤學 | GTPase | 找出 Sotorasib (AMG 510) 鎖定的 cryptic Switch-II pocket | 4OBE | 6OIM |
| BCR-ABL1 | 腫瘤學 | Tyrosine kinase | 找出 Asciminib 使用的遠端 Myristoyl pocket | 1OPL | 5MO4 |
| Cardiac Myosin | 心臟學 | Motor protein | 找出 Mavacamten 穩定 super-relaxed state 的機械調控位點 | 5TBY | 6C1H |
| c-Myc/Max heterodimer | 腫瘤學 | Transcription factor | 探索高度不可成藥標的 c-Myc 的潛在異位調控區域 | 1NKP | 依共識與 docking 可行性評估 |

c-Myc 是延伸探索標的，被認為與超過 50% 癌症失調相關，且缺乏 FDA 核准的異位抑制劑。競賽也鼓勵參賽者從 Allosteric Database (ASD) 選擇額外具有已知異位位點的蛋白質，以展示泛化能力與可擴展性。

## 輸出要求

每個目標蛋白質至少需產生以下成果：

1. **Connectivity Matrix**

   一個 `N x N` 矩陣，其中第 `(i, j)` 個元素代表殘基 `i` 與殘基 `j` 之間的量子連通強度。`N` 通常代表抽象後的殘基、節點或 coarse-grained 單元數量。

2. **Hit List**

   每個目標蛋白質的前 5 名預測異位位點，需以殘基索引或可追蹤到 PDB 結構的位置表示。

3. **Methodological Report**

   一份方法說明，解釋所選量子 metric、蛋白質結構如何轉換成量子問題、為何該 metric 可代表生物訊號傳播，以及方法與硬體限制、雜訊、可擴展性之間的關係。

## 限制條件與假設

- 可使用 gate-based quantum、quantum-inspired 或 hybrid quantum-classical 方法，但需提出可信的近期或容錯量子硬體執行路徑。
- 深度過深且未最佳化、難以在近期硬體 coherence time 內執行的電路會被扣分。
- 不得使用古典分子動力學軌跡作為輸入；目標是從拓撲結構 ab initio 預測動態訊號。
- 競賽基礎設施提供 AWS Braket 與 Classiq 服務。
- 納入範圍為蛋白質 catalytic domains。
- 排除水分子、co-factors 與複雜轉譯後修飾；除非這些因素被簡化建模為節點。
- 競賽採用 elastic network hypothesis：接觸網路拓撲是訊號傳播的主要驅動因素，因此可先抽象掉完整原子力場。

## 評量標準

官方文件強調的核心評量是 **預測準確率**，也就是演算法是否能把已知實驗驗證的異位位點排在高分位置。可推定的評估重點包含：

- 已知異位殘基或口袋是否出現在 top-ranked hit list。
- 已知遠端調控殘基的分數是否顯著高於隨機背景殘基。
- 是否能區分真正功能性異位口袋與非功能性表面口袋。
- 方法在不同蛋白質類別上的泛化能力。
- 在雜訊與硬體限制下的穩定性。
- coarse-graining 是否保留蛋白質接觸網路的關鍵拓撲訊號。
- 指標與生物學機制之間的可解釋性。
- 是否提供可被藥物發現團隊直接使用的 3D 視覺化或 residue-level mapping。

對 c-Myc 這類缺乏明確藥物結合驗證結構的標的，評估將更偏向得獎團隊間的預測共識與理論 docking 可行性。

## 建議解題方向

可行的開發路線可拆成以下模組：

1. **結構前處理**

   下載並清理 PDB 結構，移除不納入範圍的水分子、配體或複雜修飾，並建立殘基層級或 coarse-grained 節點。

2. **蛋白質接觸網路建模**

   依據 C-alpha 距離、重原子接觸、彈性網路模型或其他拓撲規則建立 adjacency matrix、Laplacian 或 weighted graph。

3. **量子映射與電路設計**

   將接觸網路轉換為 Hamiltonian、量子 walk、量子 channel、變分電路或其他量子資訊傳播模型。

4. **連通性指標計算**

   從活性位點或功能位點出發，計算殘基間的傳播強度、到達機率、相關性、保真度、干涉特徵或其他可解釋 metric。

5. **排名與驗證**

   產生 top 5 candidate residues/sites，與 holo 結構中的已知異位 pocket 或 literature annotation 比對。

6. **可視化與報告**

   將分數映射回 3D 蛋白質結構，輸出圖像、表格與方法報告，讓非量子背景的藥物研發人員也能理解結果。

## 交付物建議

建議 repository 後續維持以下結構：

```text
docs/
  cleveland-clinic-quantum-ai-challenge-2026-statement.pdf
  cleveland-clinic-quantum-ai-challenge-2026-details.zh-TW.md
data/
  <pdb_id>/
    raw/
    processed/
src/
  preprocessing/
  graph/
  quantum/
  evaluation/
notebooks/
results/
```

其中 `docs/` 保存競賽原始說明與整理後的需求文件；`data/` 保存 PDB 與衍生資料；`src/` 放可重現的程式碼；`results/` 放各標的的連通矩陣、hit list、圖像與報告輸出。

## 開發注意事項

- 檔名建議使用小寫英文與 kebab-case，方便跨平台維護與腳本化處理。
- 每個 PDB target 應保留可追蹤的來源、處理流程與 residue indexing 對應表。
- 評估時要特別注意 apo 與 holo 結構之間的殘基編號差異、缺失片段、chain selection 與 ligand binding site annotation。
- 若使用量子雲端服務，應記錄 backend、shots、noise model、transpilation 設定與隨機種子。
- 報告中應明確區分「演算法預測結果」、「文獻已知事實」與「推論或假設」。
