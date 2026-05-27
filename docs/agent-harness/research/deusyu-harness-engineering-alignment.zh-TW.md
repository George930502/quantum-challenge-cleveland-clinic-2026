# deusyu/harness-engineering 對齊稽核

稽核日期：2026-05-27。

來源 repo：`deusyu/harness-engineering`，commit `0b1f0445e2e587dd15c9c2a9dbb430f649942f8a`。

本文記錄對該 repo 內 harness engineering 文件的掃描結果、抽取出的最佳實踐，以及本 repo 已採納或新增補強的 harness artifact。它是 `external-harness-resource-synthesis.zh-TW.md` 的具體 upstream 對齊稽核。

## 掃描範圍

| 區域 | 檔案 | Harness 相關重點 |
| --- | --- | --- |
| Root | `README.md`, `README.en.md`, `AGENTS.md` | repo 作為記錄系統、root `AGENTS.md` 作為 map、機械化一致性檢查、Ralph loop 對應表。 |
| `concepts/` | `00-overview.md` 至 `07-spec-as-product.md`, `AGENTS.md` | 六大概念、Fowler guide/sensor 矩陣、機械化執行、agent readability、spec as product。 |
| `thinking/` | `cross-article-insights.md`, `evaluation-elephant-in-the-room.md`, `guides-sensors-meets-claude-code-harness.md`, `harness-for-solo-developers.md`, `harnessability-and-java.md`, `meta-harness-tensions.md`, `software-project-complexity-in-the-ai-era.md`, `why-this-project-exists.md`, `AGENTS.md` | harness 生命周期、行為評估缺口、可駕馭性、複雜度、meta-harness 張力。 |
| `practice/` | `01-ralph-demo/README.md`, `AGENTS.md` | Ralph-style Planner/Builder/Critic/Finalizer loop、scratchpad durable memory、明確 completion signal、backpressure gate。 |
| `feedback/` | `2026-04-14-translation-as-harness.md`, `AGENTS.md` | 非程式任務也能 harness 化；術語表、分段流程、回饋飛輪與並行 agent 的映射。 |
| `prompts/` | `deep-research-tracker.md`, `AGENTS.md` | prompt tracker 作為研究控制面：去重權威、信源分層、輸出 schema、定期 refresh workflow。 |
| `references/` | `articles.md`, `AGENTS.md` | external reference index 作為 single source of truth；下游快取必須同步更新。 |
| `tools/` | `00-overview.md`, `AGENTS.md` | 工具不是 awesome-list，而是對複雜度維度的具體槓桿。 |
| `works/` | 12 篇翻譯與 1 篇中文詮釋, `AGENTS.md` | 可獨立理解的作品輸出；翻譯計數納入一致性檢查，避免展示層漂移。 |
| Operational | `scripts/check-consistency.sh`, `.githooks/pre-commit`, `.github/workflows/consistency.yml` | 七層漂移檢查、本地 pre-commit、CI fallback。 |

## 抽取出的最佳實踐

1. **Repo 是 agent 的系統記錄。** 規格、決策、狀態、任務描述、驗證結果都應版本化；聊天記憶與外部文件不能作為唯一來源。
2. **Root `AGENTS.md` 是地圖，不是百科全書。** 入口文件保持短小，透過 nested `AGENTS.md`、codebase map、workflow、schema、review checklist 做漸進披露。
3. **Guide 和 sensor 必須成對。** `AGENTS.md`、spec、workflow 是前饋；typecheck、lint、schema validation、review gate、CI 是回饋。
4. **機械化檢查優先守住會漂移的不變式。** 文件數量、索引快取、reference count、內部連結、schema 欄位、完成信號都應被 deterministic check 捕捉。
5. **Ralph-style loop 需要角色分離、durable scratchpad、backpressure gate 和 completion signal。** 長任務不能只靠 agent 自評；至少要有 builder/reviewer 或 prediction/scoring 的職責分離。
6. **Prompt tracker 是研究控制面。** 定期外部掃描應有信源分層、已知內容去重清單、輸出格式、品質門檻與收錄決策，而不是臨時搜尋。
7. **Entropy management 是持續背景工作。** 反覆錯誤要升級為 guide 或 sensor；過時 harness component 要刪減；壞模式會被 agent 複製。
8. **Spec as product 讓工作流可移植。** 好的 spec 定義問題、邊界、輸入輸出與驗證形狀，不綁死實作路徑。

## 本 Repo 對齊狀態

| 實踐 | 目前狀態 | 補強決策 |
| --- | --- | --- |
| Repo-local guidance | 已有 root/nested `AGENTS.md`、`README.md`、codebase map。 | 維持 root lean；細節留在 `docs/agent-harness/`。 |
| Progressive disclosure | 已有 `docs/agent-harness/navigation/codebase-map.md` 與 placement guide。 | 新增本文件與 operation loop，避免把 upstream 掃描結果塞進 root。 |
| Guide + sensor | 已有 blueprint、state、review checklist、schema、`make validate`。 | 將 operation loop 納入 required harness docs；新增 hook/CI fallback。 |
| Mechanical drift checks | 已有 `scripts/harness/check_harness_docs.py`。 | 擴充 required files，檢查 CI workflow、pre-commit hook、Makefile hook target 與 run trace schema。 |
| Durable state | 已有 `challenge-harness-state.md`。 | Operation loop 明確規定何時更新 state、何時新增 review artifact。 |
| Ralph loop | 尚未顯式落地。 | 新增 `harness-operations-loop.zh-TW.md`，用於長任務的 role split、backpressure 和 completion signal。 |
| Prompt tracker | 尚未顯式落地。 | Operation loop 加入 harness research refresh prompt 形狀與收錄決策流程。 |
| Reference single source | 已有 external synthesis，但未標記 deusyu 稽核版本。 | 本文件固定 upstream commit 與完整掃描範圍。 |
| CI fallback | 原先無 `.github/workflows/`。 | 新增 `harness.yml`，在 push/PR 時跑 setup 與 validate。 |
| Local hook | 原先無 `.githooks/`。 | 新增 pre-commit，觸及 harness/docs/scripts 時跑便宜 gate。 |

## Challenge-Specific Adoption Rules

- 所有方法探索都應先寫清楚 allowed blind inputs 與 forbidden validation inputs。
- 每個新的 workflow 必須能指出至少一個 deterministic sensor；若只能靠人工判斷，應明確標為 inferential review。
- 每個 serious run 應能產出 eval trace 或 run metadata；沒有 trace 的結果只能視為 scratch result。
- 長任務可採 Ralph-style loop，但完成信號必須是 repo artifact 或驗證命令通過，而不是文字承諾。
- 外部 harness research refresh 只更新 `research/` 或 `workflows/` 文件；不得改動 source RCSB artifacts。

## Remaining Gaps

- `make eval` 尚未存在；等 scoring harness 完成後再新增。
- run trace JSONL registry 尚未聚合；目前只要求 per-run metadata 與 schema 相容。
- 行為 harness 仍是弱點：生物學正確性與競賽有效性需要 domain review，不應假裝 deterministic check 已覆蓋。
- Harness coverage 尚未量化；後續可新增「哪些 guide 有對應 sensor」的矩陣檢查。

## Source Links

- `deusyu/harness-engineering`: <https://github.com/deusyu/harness-engineering>
- Root README: <https://github.com/deusyu/harness-engineering/blob/main/README.md>
- Root AGENTS: <https://github.com/deusyu/harness-engineering/blob/main/AGENTS.md>
- Concepts directory: <https://github.com/deusyu/harness-engineering/tree/main/concepts>
- Ralph demo: <https://github.com/deusyu/harness-engineering/tree/main/practice/01-ralph-demo>
- Deep research tracker: <https://github.com/deusyu/harness-engineering/blob/main/prompts/deep-research-tracker.md>
- Consistency check: <https://github.com/deusyu/harness-engineering/blob/main/scripts/check-consistency.sh>
