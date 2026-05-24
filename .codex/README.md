# Codex Local Environment

This directory documents the shared Codex app setup for the repository.

Recommended local environment setup script:

```sh
sh .codex/setup.sh
```

Recommended Codex app actions:

| Action | Command |
| --- | --- |
| Setup | `make setup` |
| Validate | `make validate` |
| Analyze | `make analyze` |

Keep setup deterministic and offline by default. Data refreshes use the network and should stay explicit:

```sh
python3 scripts/download_allosteric_challenge_rcsb.py
```
