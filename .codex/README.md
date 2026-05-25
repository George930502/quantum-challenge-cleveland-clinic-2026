# Codex Local Environment

This directory documents the shared Codex app setup for the repository.

Recommended local environment setup script:

```sh
sh .codex/setup.sh
```

After setup, install local language-server tooling when the workspace needs type checking:

```sh
make lsp
```

Recommended Codex app actions:

| Action | Command |
| --- | --- |
| Setup | `make setup` |
| LSP | `make lsp` |
| Typecheck | `make typecheck` |
| Harness Check | `make harness-check` |
| Validate | `make validate` |
| Analyze | `make analyze` |
| Diff Check | `git diff --check` |
| Harness Orient | `sed -n '1,220p' docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md` |
| Harness State | `sed -n '1,220p' docs/agent-harness/state/challenge-harness-state.md` |

Keep setup deterministic and offline by default. Data refreshes use the network and should stay explicit:

```sh
python3 scripts/pipeline/download_allosteric_challenge_rcsb.py
```

For long-running challenge-method work, use `docs/agent-harness/state/challenge-harness-state.md` as the handoff file and keep validation scoring separate from blind feature extraction.
