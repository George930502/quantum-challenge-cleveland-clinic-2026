# Harness Operations Loop

本文把 `deusyu/harness-engineering` 中的 Ralph loop、prompt tracker、guide/sensor、entropy management 實踐，轉成此量子挑戰賽 repo 的日常操作流程。

## Loop 0: Session Orientation

每個 broad task 先讀：

1. `AGENTS.md`
2. `docs/agent-harness/navigation/codebase-map.md`
3. 最近的 nested `AGENTS.md`
4. `docs/agent-harness/state/challenge-harness-state.md`
5. 任務對應 workflow 或 review checklist

完成條件：

- 能指出 active dataset slugs。
- 能區分 source artifacts、generated outputs、human-authored docs。
- 能說明 validation labels 不可進入 blind feature extraction。

Sensor：

```sh
make harness-check
```

## Loop 1: Research Or Build Work Package

每個 work package 應拆成四個角色，可以由同一個 agent 分階段執行，也可以由多代理並行：

| Role | Responsibility | Required artifact |
| --- | --- | --- |
| Planner | 定義問題、允許輸入、禁止輸入、輸出格式與驗證方式。 | workflow section、issue、或 state entry。 |
| Builder | 實作或撰寫文件，只處理當前 scope。 | code/doc diff。 |
| Critic | 重跑 deterministic checks，檢查資料洩漏、schema、provenance。 | review note 或 final summary。 |
| Finalizer | 更新 durable state，列出驗證命令與殘留風險。 | `challenge-harness-state.md` 或 review artifact。 |

Backpressure gates：

```sh
make harness-check
git diff --check
make validate
```

對 docs-only work，至少跑 `git diff --check` 與 `make harness-check`。對 scripts 或 generated outputs，跑 `make validate`。

Completion signal：

- deterministic command passes；或
- 明確 review artifact 寫下「未通過」原因與下一步；或
- state file 更新 blocker，不能用口頭承諾代替。

## Loop 2: Method Run Discipline

Prediction method 必須分成兩段：

| Stage | Allowed inputs | Forbidden inputs |
| --- | --- | --- |
| Blind feature extraction | input apo structures、permitted metadata、input-chain contact graphs。 | validation ligand coordinates、validation contact residues、holo-only ligand metadata。 |
| Validation scoring | 已產生的 prediction outputs、validation labels。 | 回寫到 feature extraction 的任何 label-derived feature。 |

每個 serious run 應留下：

- run directory 或 summary path。
- method name、version、parameters、seed。
- input graph path 與 explicitly excluded validation paths。
- output matrix / hit list / report paths。
- verification command 與 exit status。

Sensor：

```sh
python3 scripts/harness/check_harness_docs.py
python3 scripts/pipeline/analyze_allosteric_challenge_datasets.py
```

後續 scoring harness 完成後，新增 `make eval` 並把它納入 `make validate` 或 release gate。

## Loop 3: Harness Research Refresh

每 1-2 週或遇到重要 upstream 更新時執行。目標是更新 harness knowledge，而不是臨時堆 prompt。

Search prompt shape：

```text
搜尋最近 {START_DATE} 至 {END_DATE} 的 harness engineering / context engineering /
agent evaluation / coding-agent orchestration 高價值內容。

必須輸出：
- title, URL, author/org, date
- source tier
- 3-5 core insights
- 與本 repo 既有 harness docs 的關聯
- 收錄 / 觀察 / 不採納建議

排除：
- 純產品公告
- 沒有新觀點的翻譯或摘要
- 與 agent harness 只有表面關聯的內容
```

Analysis prompt shape：

```text
請把搜尋結果對照本 repo 的 harness artifact：
- AGENTS.md and nested AGENTS.md
- docs/agent-harness/navigation/codebase-map.md
- docs/agent-harness/workflows/*.md
- docs/agent-harness/state/challenge-harness-state.md
- docs/agent-harness/schemas/eval-trace.schema.json
- scripts/harness/check_harness_docs.py

輸出：
1. 值得採納的 practice
2. 不採納原因
3. 需要新增 guide 的項目
4. 需要新增 deterministic sensor 的項目
5. 是否更新 state / review checklist / Makefile
```

收錄規則：

- 外部資料摘要放 `docs/agent-harness/research/`。
- 可重複流程放 `docs/agent-harness/workflows/`。
- mutable task memory 只放 `docs/agent-harness/state/`。
- 不把長篇外部文章貼入 repo；只保留摘要、採納決策與 source links。

## Loop 4: Entropy Management

每當同類錯誤出現第二次，必須做一次 harness decision：

| Symptom | Preferred fix |
| --- | --- |
| Agent 反覆讀錯檔案 | 更新 codebase map 或 nested `AGENTS.md`。 |
| Agent 反覆忘記資料邊界 | 更新 workflow guide，並新增 deterministic leakage check。 |
| Generated outputs 漂移 | 將 schema 或 file naming 納入 `check_harness_docs.py`。 |
| Review 發現同類科學風險 | 更新 review checklist 或新增 domain-specific review artifact。 |
| Harness 文件彼此矛盾 | 指定 single source of truth，其他文件只做 summary/cache。 |

刪減規則：

- 若新模型或新 workflow 讓某個 harness component 不再承重，先在 state 或 review note 記錄，再移除或降級。
- 不保留「也許有一天會用到」的 framework、skill、MCP 或依賴。

## Current Minimum Harness

本 repo 的最小完成門檻是：

```sh
make setup
make lsp
make validate
```

本地 hook 可用：

```sh
make install-hooks
```

CI fallback 由 `.github/workflows/harness.yml` 執行，確保未啟用本地 hook 時仍有合併門。
