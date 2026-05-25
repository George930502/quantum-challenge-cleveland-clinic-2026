# Agent Harness Index

This directory contains agent-harness guidance for the challenge workspace. Keep this root as an index; place detailed documents in the most specific subdirectory.

## Directory Layout

| Directory | Purpose | Start with |
| --- | --- | --- |
| `navigation/` | Repository maps, placement rules, and orientation material. | `navigation/codebase-map.md` |
| `workflows/` | Agent workflow blueprints and reusable operating procedures. | `workflows/quantum-challenge-harness.zh-TW.md` |
| `state/` | Durable working state for long-running challenge tasks. | `state/challenge-harness-state.md` |
| `schemas/` | Machine-readable contracts for eval traces and future run records. | `schemas/eval-trace.schema.json` |
| `reviews/` | Review checklists and publishing gates. | `reviews/code-review-checklist.md` |
| `research/` | Synthesis of external harness-engineering sources. | `research/external-harness-resource-synthesis.zh-TW.md` |

## Placement Rules

- New navigation maps go in `navigation/`.
- New file-placement or repository-structure rules go in `navigation/`.
- New repeatable agent workflows go in `workflows/`.
- Mutable handoff or task-state files go in `state/`.
- JSON schemas and other contracts go in `schemas/`.
- Review rubrics and release gates go in `reviews/`.
- Literature or web-source synthesis goes in `research/`.

Run `make harness-check` after changing this directory.
