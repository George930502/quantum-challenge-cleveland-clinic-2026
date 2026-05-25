# AGENTS.md

## Scope

`docs/` contains grouped challenge notes, research synthesis documents, review guidance, and agent harness documentation. Most research prose is Traditional Chinese.

## Directory Layout

- `challenge/`: original challenge statement and competition-specific notes.
- `research/`: cross-dataset synthesis and research-facing reports.
- `agent-harness/`: Codex guidance, codebase maps, and review checklists.

## Rules

- Preserve Traditional Chinese for existing `.zh-TW.md` documents.
- Keep operational agent guidance concise and link to detailed references instead of duplicating full source articles.
- Use relative links when referencing repository files.
- Keep new documents in the most specific subdirectory instead of adding more files directly under `docs/`.
- Do not paste long copyrighted source excerpts. Summarize and cite URLs.

## Verification

- Run `git diff --check` for documentation-only edits.
- If documentation describes generated outputs, verify filenames exist with `rg --files`.
