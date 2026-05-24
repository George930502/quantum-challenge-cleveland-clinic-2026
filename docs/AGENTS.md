# AGENTS.md

## Scope

`docs/` contains challenge notes, synthesis documents, review guidance, and agent harness documentation. Most prose is Traditional Chinese.

## Rules

- Preserve Traditional Chinese for existing `.zh-TW.md` documents.
- Keep operational agent guidance concise and link to detailed references instead of duplicating full source articles.
- Use relative links when referencing repository files.
- Do not paste long copyrighted source excerpts. Summarize and cite URLs.

## Verification

- Run `git diff --check` for documentation-only edits.
- If documentation describes generated outputs, verify filenames exist with `rg --files`.
