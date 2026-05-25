# Repository Structure And Placement Guide

本文定義此 repo 日後新增檔案的位置規則，避免把不同用途的檔案塞在同一層 root。規則依據 Python Packaging User Guide 的 flat/src layout 討論、setuptools package discovery 文件、Diataxis 文件架構方法，以及 harness engineering 的 progressive disclosure 原則整理。

## 設計原則

1. Root 只放專案入口與跨工具配置，例如 `README.md`, `AGENTS.md`, `Makefile`, `requirements.txt`, `package.json`, `pyrightconfig.json`。
2. 可執行腳本按職責分組，不把 pipeline、harness maintenance、一次性工具混在 `scripts/` root。
3. `docs/agent-harness/` root 只放 index；詳細文件放入語意清楚的子目錄。
4. 檔名要描述文件用途，優先使用 lowercase kebab-case；schema 檔使用 `.schema.json`。
5. 可變動的 working state 與相對穩定的 workflow/spec 分開。
6. 任何新固定位置都要能被 `make harness-check` 或 `make validate` 發現問題。

## Current Top-Level Placement

| Path | What belongs here | What does not belong here |
| --- | --- | --- |
| `data/` | Checked-in source artifacts from RCSB and manifests. | Hand-edited derived analysis. |
| `analysis/` | Generated summaries, graphs, labels, future method runs. | Raw downloaded RCSB source files. |
| `docs/challenge/` | Challenge statements and challenge-specific constraints. | Agent workflow state. |
| `docs/research/` | Scientific synthesis and dataset interpretation. | Harness implementation checks. |
| `docs/agent-harness/` | Agent navigation, workflows, state, schemas, reviews, harness-source synthesis. | General research notes unrelated to agent operation. |
| `scripts/pipeline/` | Downloader, analyzer, future model/eval pipeline entrypoints. | Harness doc checks. |
| `scripts/harness/` | Fast repo-maintenance and harness-invariant checks. | RCSB download or scientific analysis logic. |
| `.codex/` | Codex local environment notes and setup shell. | General scripts or generated outputs. |

## Scripts Placement

| New file type | Location | Naming example |
| --- | --- | --- |
| RCSB/data refresh script | `scripts/pipeline/` | `download_allosteric_challenge_rcsb.py` |
| Derived analysis generator | `scripts/pipeline/` | `analyze_allosteric_challenge_datasets.py` |
| Future model runner | `scripts/pipeline/` | `run_quantum_walk_baseline.py` |
| Future scorer/evaluator | `scripts/pipeline/` | `score_residue_hit_lists.py` |
| Harness documentation check | `scripts/harness/` | `check_harness_docs.py` |
| Future repository structure check | `scripts/harness/` | `check_repository_structure.py` |

If pipeline scripts grow shared code, create a package-like subdirectory under `scripts/pipeline/` or move importable code to a future `src/` package with explicit packaging config. Do not place importable libraries directly in repository root.

## Agent Harness Docs Placement

| New document type | Location | Naming example |
| --- | --- | --- |
| Repository map or placement rule | `docs/agent-harness/navigation/` | `repository-structure-placement-guide.zh-TW.md` |
| Repeatable agent workflow | `docs/agent-harness/workflows/` | `quantum-challenge-harness.zh-TW.md` |
| Durable task state or handoff | `docs/agent-harness/state/` | `challenge-harness-state.md` |
| JSON schema or data contract | `docs/agent-harness/schemas/` | `eval-trace.schema.json` |
| Review checklist or release gate | `docs/agent-harness/reviews/` | `code-review-checklist.md` |
| External source synthesis | `docs/agent-harness/research/` | `external-harness-resource-synthesis.zh-TW.md` |

## Naming Rules

- Use descriptive nouns: `codebase-map`, `challenge-harness-state`, `code-review-checklist`.
- Avoid opaque abbreviations unless they are established dataset slugs or tool names.
- Prefer lowercase kebab-case for new Markdown files.
- Preserve `.zh-TW.md` for Traditional Chinese prose.
- Use `.schema.json` for JSON schema contracts.
- Avoid uppercase filenames for new files except `AGENTS.md`, `README.md`, and externally imposed conventions.

## Update Checklist

When moving or adding files:

1. Update `README.md`, `AGENTS.md`, and nearest nested `AGENTS.md`.
2. Update `docs/agent-harness/README.md` and `docs/agent-harness/navigation/codebase-map.md` if this affects navigation.
3. Update `Makefile` if command paths changed.
4. Update `scripts/harness/check_harness_docs.py` if the file is a harness invariant.
5. Run `make harness-check`.
6. Run `make validate` for scripts, generated output, or structural changes.

## Sources

- Python Packaging User Guide, `src layout vs flat layout`: <https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/>
- Setuptools package discovery documentation: <https://setuptools.pypa.io/en/latest/userguide/package_discovery.html>
- Diataxis documentation architecture: <https://diataxis.fr/>
- `walkinglabs/awesome-harness-engineering`: <https://github.com/walkinglabs/awesome-harness-engineering>
