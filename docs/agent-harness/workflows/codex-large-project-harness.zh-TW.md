# Codex 大型專案 Harness 最佳實踐

本文把 Anthropic 的大型 codebase Claude Code 文章觀察，對照 OpenAI Codex 官方文件，整理成這個 repository 已採用的 agent harness 設計。

## 來源洞見

Claude 文章的核心結論是：大型專案裡，模型能力不是唯一瓶頸，真正決定表現的是模型外圍的 harness。文章把 harness 拆成分層指令檔、hooks、skills、plugins、MCP、LSP 與 subagents，並強調 codebase 必須先變得可導航，否則 agent 會把 context 花在找路而不是解題。

OpenAI Codex 文件給出的對應實踐是：

- 使用 `AGENTS.md` 做 durable project guidance，並利用 root 到當前目錄的分層載入機制。
- 用 prompt 明確交代 goal、context、constraints、done when。
- 針對複雜任務先 planning，再 implementation。
- 透過 sandbox 與 permissions 維持 least privilege。
- 用 local environments/actions 固化 setup、build、test 等常用動作。
- 用 review、tests、lint、format/type check 定義完成標準。
- 外部且會變動的資訊用 MCP，不要手動貼進 prompt。
- 重複性流程升級成 skills，穩定週期工作再升級成 automations。
- read-heavy 或 noisy exploration 可交給 subagents，主 thread 保留決策與最終輸出。

## 本 Repo 的落地設計

### 1. 分層 `AGENTS.md`

本 repo 新增 root `AGENTS.md`，提供所有 session 都需要知道的高層資訊：專案目的、資料夾角色、驗證命令、資料不可手改等規則。

另外在 `data/`、`analysis/`、`docs/`、`scripts/` 各放一份局部 `AGENTS.md`：

- `data/AGENTS.md`：要求 source artifacts 只能用 downloader refresh，不手改大型結構檔。
- `analysis/AGENTS.md`：要求 generated outputs 由 analyzer 產生，並維持檔名穩定。
- `docs/AGENTS.md`：要求既有中文文件維持繁體中文，避免長篇引用外部文章。
- `scripts/AGENTS.md`：要求 deterministic output、更新 dependency 時同步文件。

這符合「root 檔保持精簡、細節放到靠近工作區的文件」的原則。

### 2. Codebase Map

`docs/agent-harness/navigation/codebase-map.md` 是 agent 的目錄地圖。大型專案常見問題不是資料不存在，而是 agent 一開始不知道該讀哪裡。這份 map 讓 Codex 可以先判斷：

- 哪些資料夾是 source input、generated output、docs、pipeline。
- 三個 dataset slug 對應的 PDB ID、domain、primary question。
- 面對大型 PDB/mmCIF/XML/PDF gzip 時應先讀 manifest 或 JSON summary，而不是直接塞滿 context。

### 3. 驗證與 Review 標準

`Makefile` 提供最小可重複命令：

- `make setup`
- `make analyze`
- `make validate`

`docs/agent-harness/reviews/code-review-checklist.md` 把 review 標準拆成 scientific correctness、reproducibility、agent harness、git hygiene。Codex 文件建議把 review guidance 放在 repo 中並由 `AGENTS.md` 引用，這樣 review 行為才能跨 session 一致。

### 4. Harness Environment

本 repo 使用 `.codex/README.md` 與 `.codex/setup.sh` 描述 Codex App local environment 的建議設定，而不是假造 app-specific schema。Codex App 的 local environments/actions 應在 App settings 中產生共享配置；若要建立 worktree setup script，本 repo 的建議腳本是：

```sh
sh .codex/setup.sh
```

它只安裝 `requirements.txt`，避免在新 worktree 裡做不可預期的資料下載。

### 5. Context Hygiene

這個 repo 有大量結構資料。對 agent 而言，最佳預設不是「讀完整 data/」，而是：

1. 讀 `AGENTS.md`。
2. 讀 `docs/agent-harness/navigation/codebase-map.md`。
3. 針對任務讀最近的 nested `AGENTS.md`。
4. 先看 manifests、summary JSON、CSV header 或 targeted `rg`。
5. 只有需要精確座標或 metadata 時才讀大型 PDB/mmCIF/XML。

### 6. 未來可擴充項

- 若常做「新增 dataset」流程，可把它包成 repo-local skill。
- 若常做「每週資料 refresh 與差異摘要」，可做 Codex automation。
- 若要讓 Codex 查 challenge portal、GitHub issue、internal notes，應用 MCP，而不是把外部狀態複製到文件。
- 若 Python pipeline 擴大，可加入 `ruff`、`pytest` 與型別檢查，並把命令寫回 `AGENTS.md`。

### 7. Challenge-Specific Harness

本 repo 另有 `docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md`，把 `walkinglabs/awesome-harness-engineering` 中的 context management、safe autonomy、spec workflow、eval/observability、runtime harness 原則，落地成此量子挑戰賽專用配置。外部資源稽核與採納矩陣見 `docs/agent-harness/research/external-harness-resource-synthesis.zh-TW.md`。

新增的 durable state 與評估入口是：

- `docs/agent-harness/state/challenge-harness-state.md`：長任務交接、工作包狀態、已知風險與下一步。
- `docs/agent-harness/schemas/eval-trace.schema.json`：未來 method run / scoring trace 的最小 JSON schema。
- `scripts/harness/check_harness_docs.py` 與 `make harness-check`：把必要 harness artifacts、schema 形狀與內部連結轉成 deterministic check。

這讓後續 quantum-inspired method、baseline、scoring harness 可以在不污染 blind input feature 的前提下，留下可重跑、可審查的輸入輸出與驗證紀錄。

## 參考來源

- Anthropic: <https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start>
- OpenAI Codex AGENTS.md: <https://developers.openai.com/codex/guides/agents-md>
- OpenAI Codex Best Practices: <https://developers.openai.com/codex/learn/best-practices>
- OpenAI Codex Workflows: <https://developers.openai.com/codex/workflows>
- OpenAI Codex Local Environments: <https://developers.openai.com/codex/app/local-environments>
- OpenAI Codex Permissions: <https://developers.openai.com/codex/permissions>
- OpenAI Codex Subagents: <https://developers.openai.com/codex/concepts/subagents>
- WalkingLabs Awesome Harness Engineering: <https://github.com/walkinglabs/awesome-harness-engineering>
