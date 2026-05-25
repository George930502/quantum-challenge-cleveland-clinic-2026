# Quantum Challenge Harness Blueprint

本文把 `walkinglabs/awesome-harness-engineering` 彙整的 harness engineering 原則，落地成此 repo 面向 Cleveland Clinic 2026 quantum AI challenge 的 agent 工作環境。外部資源逐項稽核與採納決策見 `docs/agent-harness/research/external-harness-resource-synthesis.zh-TW.md`。

## 來源原則

`awesome-harness-engineering` 對 harness engineering 的核心定義是：設計 AI agent 外圍的工作環境，讓 agent 在真實、長時間、可驗證的工作流中更可靠。該 repo 將最佳實踐分成幾個面向：

- Context, memory, and working state: 把 context window 當成有限工作記憶，使用 repo-local files 保存 durable state。
- Constraints, guardrails, and safe autonomy: 讓 agent 有足夠工具完成任務，但用 sandbox、明確權限、資料邊界與驗證命令限制風險。
- Specs, agent files, and workflow design: 用 `AGENTS.md`、spec、checklist、task state 定義可重複流程，而不是把規則藏在單次 prompt。
- Evals and observability: 把每次研究/程式改動留下可檢查的輸入、輸出、指標、失敗原因與驗證命令。
- Runtimes and reference implementations: 將 setup、test、typecheck、analysis、review 固化成穩定命令，降低 session-to-session drift。

本 repo 不需要引入大型 agent framework；更適合採用輕量、檔案式、可審查的 research harness。

## Challenge-Specific Harness Goals

此挑戰賽的成功條件不是只產生一段程式，而是長期收斂出一套可信的量子或量子啟發式異位位點預測流程。因此 harness 的主要目標是：

1. 防止資料洩漏：apo input structure 可作為 blind input；holo validation ligand 只能作為 validation label 或 sanity check。
2. 保留科學 provenance：任何 ranking、matrix、hit list 都要能追到 dataset slug、PDB ID、chain、residue numbering、script version 與輸入檔。
3. 支援長任務續接：方法探索、失敗嘗試、待確認假設與下一步要寫在 durable state，不依賴聊天上下文。
4. 讓評估可重跑：每個候選方法至少要產生 deterministic outputs、固定 metric 與 baseline comparison。
5. 控制探索成本：大型 PDB/mmCIF/XML 只用 targeted reads；新增依賴或網路資料必須是明確、可辯護的工作包。

## Harness Architecture

| Layer | Repo artifact | Purpose |
| --- | --- | --- |
| Entry instructions | `AGENTS.md`, nested `AGENTS.md` | Stable rules, data boundaries, verification commands. |
| Navigation map | `docs/agent-harness/navigation/codebase-map.md` | Compact map before opening large data files. |
| Challenge spec | `docs/challenge/cleveland-clinic-quantum-ai-challenge-2026-details.zh-TW.md` | Task objective, inputs, outputs, restrictions, scoring criteria. |
| Research summary | `docs/research/allosteric-challenge-three-dataset-feature-analysis.zh-TW.md` | Dataset facts and validation caveats. |
| Working state | `docs/agent-harness/state/challenge-harness-state.md` | Durable memory for active hypotheses, work packages, blockers, and handoff notes. |
| Eval trace schema | `docs/agent-harness/schemas/eval-trace.schema.json` | Minimal record format for method runs and agent-assisted experiments. |
| Runtime commands | `Makefile`, `.codex/setup.sh`, `.codex/README.md` | Setup, typecheck, analysis, validation, and local environment actions. |
| Harness invariant check | `scripts/harness/check_harness_docs.py`, `make harness-check` | Deterministic guard for required harness docs, schema shape, and internal links. |
| Review gate | `docs/agent-harness/reviews/code-review-checklist.md` | Scientific, reproducibility, harness, and git hygiene checklist. |

## Recommended Work Packages

### 1. Orientation Package

Use when a new agent/session enters the repo.

Inputs:

- `AGENTS.md`
- `docs/agent-harness/navigation/codebase-map.md`
- `docs/challenge/cleveland-clinic-quantum-ai-challenge-2026-details.zh-TW.md`
- `docs/agent-harness/state/challenge-harness-state.md`

Done when:

- The agent can name the active dataset slugs: `kras_g12c`, `bcr_abl1`, `cardiac_myosin`.
- The agent can state which files are source artifacts, generated outputs, and human-authored notes.
- The agent knows not to use validation ligands as blind input features.

### 2. Dataset Analysis Package

Use when changing downloader/analyzer behavior or adding a dataset.

Inputs:

- `scripts/AGENTS.md`
- `scripts/pipeline/analyze_allosteric_challenge_datasets.py`
- `scripts/pipeline/download_allosteric_challenge_rcsb.py`
- `data/<dataset_slug>/rcsb/**/_download_manifest.json`

Required outputs:

- Updated dataset specs in scripts.
- Generated summaries under `analysis/<dataset_slug>/`.
- Cross-dataset summary update if dimensions or validation labels change.

Verification:

```sh
make typecheck
make validate
```

### 3. Method Exploration Package

Use when adding a quantum, quantum-inspired, or classical baseline method.

Boundary terms used throughout this repo:

- `blind feature extraction`: model input construction from apo structures and permitted metadata only.
- `validation scoring`: evaluation against holo validation labels after predictions are already produced.

Inputs:

- Apo structure only as blind model input.
- Residue contact graph CSVs generated from input chains.
- Validation contact CSVs only inside scoring/evaluation code paths.

Required outputs:

- Connectivity matrix.
- Residue-level ranked hit list.
- Method metadata: graph construction, coarse-graining, Hamiltonian/quantum-walk or baseline definition, random seeds, parameter grid.
- Eval trace entry matching `docs/agent-harness/schemas/eval-trace.schema.json`.

Verification:

```sh
make validate
```

Additional checks for modeling code should include deterministic rerun comparison and at least one random or graph-centrality baseline.

### 4. Scientific Review Package

Use before treating a method result as competition-facing evidence.

Review questions:

- Are validation ligands used only for labels/scoring?
- Are residue IDs traceable to PDB chain and residue numbers?
- Does the method avoid classical MD trajectory inputs?
- Is the metric biologically interpretable as allosteric signal propagation, not just generic centrality?
- Are noise, coarse-graining, and scalability claims supported by outputs or bounded assumptions?
- For `cardiac_myosin`, is the 6C1H validation caveat explicitly preserved?

Verification:

```sh
git diff --check
make validate
```

## Context Discipline

Prefer this read order:

1. Root `AGENTS.md`.
2. `docs/agent-harness/navigation/codebase-map.md`.
3. Nearest nested `AGENTS.md`.
4. Dataset summary JSON or markdown.
5. CSV headers or targeted `rg` over structural files.
6. Full PDB/mmCIF/XML only when exact source inspection is required.

Avoid this:

- Reading all of `data/` into context.
- Manually editing generated CSV/JSON outputs.
- Mixing challenge labels into blind-feature extraction.
- Adding dependencies without updating setup, docs, and validation.

## Observability And Eval Records

Every serious method run should leave a compact record, either in a JSONL file under a future `analysis/<dataset_slug>/runs/` directory or in a method-specific summary generated by scripts. The record should include:

- Run identity: timestamp, git commit if available, dataset slug, input PDB, chain.
- Method identity: method name, version, parameters, random seed.
- Inputs: graph path, allowed metadata paths, explicitly excluded validation paths.
- Outputs: connectivity matrix path, hit list path, report path.
- Metrics: top-k hit overlap, enrichment against random residues, baseline comparison.
- Verification: command, exit status, important warnings.

The schema in `eval-trace.schema.json` is intentionally minimal so it can be adopted before a full experiment tracker exists.

## Tool And Skill Policy

Recommended capabilities by task:

| Task | Preferred capability |
| --- | --- |
| Repo navigation and code edits | Codex with `AGENTS.md`, `rg`, `make validate`. |
| Quantum circuit or simulator work | Repo-local scripts first; use Qiskit/Cirq/PennyLane skills only when implementation needs those APIs. |
| Literature lookup | Use current web or research lookup tools, cite primary sources, and summarize instead of pasting long excerpts. |
| RCSB or biology database refresh | Use downloader or explicit database tools; record provenance. |
| Long-running recurring refresh | Codex automation only after the exact command and review output are stable. |

## Current Recommended Harness Configuration

Codex local environment setup:

```sh
sh .codex/setup.sh
make lsp
make validate
```

Recommended Codex actions:

| Action | Command | Use |
| --- | --- | --- |
| Setup | `make setup` | Install Python runtime dependencies. |
| LSP | `make lsp` | Install local Pyright tooling. |
| Typecheck | `make typecheck` | Validate scripts without regenerating outputs. |
| Analyze | `make analyze` | Regenerate derived analysis from checked-in data. |
| Validate | `make validate` | Main offline gate before publishing. |
| Diff Check | `git diff --check` | Minimum doc-only gate. |
| Harness Check | `make harness-check` | Required harness artifact and internal-link check. |

Network-enabled action:

```sh
python3 scripts/pipeline/download_allosteric_challenge_rcsb.py
```

Keep this separate from default setup because it refreshes external scientific source artifacts.

## Upgrade Path

Add these only when the workflow needs them:

- `pytest` tests around graph construction and scoring once modeling scripts exist.
- A method-run writer that emits JSONL records matching `eval-trace.schema.json`.
- A `make eval` target after there is at least one deterministic method implementation.
- A lightweight experiment registry under `analysis/<dataset_slug>/runs/`.
- A repo-local skill for "add challenge dataset" after that workflow repeats at least twice.

## References

- `walkinglabs/awesome-harness-engineering`: <https://github.com/walkinglabs/awesome-harness-engineering>
- OpenAI, "Harness engineering: leveraging Codex in an agent-first world": <https://openai.com/index/harness-engineering/>
- Anthropic, "Effective harnesses for long-running agents": <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
- Martin Fowler / Thoughtworks, "Harness Engineering": <https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html>
